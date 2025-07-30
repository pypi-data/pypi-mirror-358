import logging
from typing import Union

from knowledgenet.ftypes import EventFact, Wrapper
from knowledgenet.tracer import trace
from knowledgenet.perm import combinations
from knowledgenet.node import Node
from knowledgenet.factset import Factset
from knowledgenet.graph import Graph, Element
from knowledgenet.container import Collector
from knowledgenet.ruleset import Ruleset

class Session:
    def __init__(self, ruleset:Ruleset, facts, id, global_ctx={}):
        self.id = id
        self.ruleset = ruleset
        self.rules = ruleset.rules
        self.global_ctx = global_ctx
        self.input_facts = facts

    def __str__(self):
        return f"Session({self.id})"
    
    def __repr__(self):
        return self.__str__()

    @trace()
    def execute(self):  
        self.output_facts = Factset()
        self.graph = Graph(id=self.id)
        logging.debug("%s: Initializing graph", self)
        leftmost,_, updated_facts = self._add_facts(self.input_facts)
        logging.debug("%s: Executing rules on graph", self)
        
        self.graph.new_cursor(element=leftmost)
        while element := self.graph.next_element():
            #print(f"Graph content: {self.graph.to_element_list(cursor_name='list')}")
            node = element.obj
            # Execute the rule on the node
            result = node.execute(self.output_facts)
            if node.rule.run_once:
                e = self.graph.delete_element(element)
                if element == leftmost:
                    leftmost = e
                element = e

            if result:
                # If the rule execution resulted in merges (insert, update, delete)
                all_updates = set()

                # The delete objects need to be handled first because the application may decided to delete a fact and then insert the same fact 
                if 'delete' in node.changes:
                    deleted_facts = node.changes['delete']
                    leftmost, deleted, updated_facts =  self._delete_facts(deleted_facts, leftmost)
                    all_updates.update(updated_facts)
                    logging.debug("%s: Deleted facts: %s", self, deleted)

                if 'insert' in node.changes:
                    new_facts = node.changes['insert']
                    leftmost, _, updated_facts = self._add_facts(new_facts, leftmost)
                    all_updates.update(updated_facts)
                    logging.debug("%s: Inserted facts: %s", self, new_facts)

                if 'update' in node.changes:
                    all_updates.update(node.changes['update'])

                if len(all_updates):
                    leftmost, _ = self._update_facts(node, all_updates, leftmost)
                    logging.debug("%s: Updated facts: %s", self, all_updates)

                if 'break' in node.changes:
                    logging.debug("%s: Breaking session: destination: next_ruleset", self)
                    break
                    
                if 'switch' in node.changes:
                    # Terminate the session execution
                    logging.debug("%s: Ending session: destination: %s", self, node.changes['switch'])
                    self.output_facts.add_facts([node.changes['switch']])
                    break

                logging.debug("%s: After all merges were completed: leftmost changed element: %s, current element: %s", self, leftmost, element)

                if element is not leftmost:
                    self.graph.new_cursor(element=leftmost)
        return self.output_facts.facts
    
    @trace()
    def _delete_facts(self, deleted_facts: Union[set,list], current_leftmost: Element)->tuple[Element:int]:
        deduped_deletes = set(deleted_facts)
        changed_collectors = self.output_facts.del_facts(deduped_deletes)
        logging.debug("%s: Iterating through graph with deleted facts: %s", self, deduped_deletes)
        cursor_name = 'merge'
        self.graph.new_cursor(cursor_name=cursor_name)
        new_leftmost = current_leftmost
        while element := self.graph.next_element(cursor_name):
            overlap = [value for value in element.obj.when_objs if value in deduped_deletes]
            if len(overlap):
                next_element = self.graph.delete_element(element)
                if element.obj == new_leftmost.obj:
                    # If the leftmost object is being deleted
                    new_leftmost = next_element
                else:
                    new_leftmost = self._minimum(new_leftmost, element)

        logging.debug("%s: Deleted facts from graph, count: %d, changed_collectors: %s, new leftmost: %s", self, len(deduped_deletes), changed_collectors, new_leftmost)
        return new_leftmost, deduped_deletes, changed_collectors

    @trace()
    def _update_facts(self, execution_node: Node, facts: Union[set,list], 
                       current_leftmost: Element)->tuple[Element:int]:
        deduped_updates = set(facts) # Remove duplicates
        updated_facts = self.output_facts.update_facts(deduped_updates)
        new_leftmost = current_leftmost
        logging.debug("%s: Iterating through graph with updated facts: %s", self, deduped_updates)
        cursor_name = 'merge'
        self.graph.new_cursor(cursor_name=cursor_name)
        node = execution_node
        while element:= self.graph.next_element(cursor_name):
            node = element.obj
            if node == execution_node and not node.rule.retrigger_on_update:
                # if this node updated the object and the rule option is not to retrigger on updare
                continue

            if node.reset_whens(deduped_updates):
                new_leftmost = self._minimum(new_leftmost, element)

        if len(updated_facts) > 0:
            logging.debug("%s: An update resulted in changes to collectors: %s", self, updated_facts)
            # As a part of updated, additional collectors may have been affected, update the graph accordingly
            new_leftmost, chg_count = self._update_facts(node, updated_facts, new_leftmost)
        logging.debug("%s: Updated graph, count: %d, updated facts: %s, new leftmost: %s", self, len(deduped_updates), deduped_updates, new_leftmost)
        return new_leftmost, deduped_updates

    def _get_matching_objs(self, rule):
        when_objs = []
        # For each class associated with the when clause, look if object(s) of that type exists. If objects exist for all of the when clauses, then this rule satisfies the need and is ready to be put in the graph
        for when in rule.whens:
            if when.of_type in (Collector,EventFact):
                objs = self.output_facts.find(when.of_type, group=when.group)
            else:
                objs = self.output_facts.find(when.of_type)
            if not objs:
                return None
            when_objs.append(objs)
        return when_objs

    @trace()
    def _add_facts(self, facts: Union[set,list], current_leftmost:Element=None)->tuple[Element:int]:
        # The new_facts variable contains a (deduped) set
        new_facts,updated_facts = self.output_facts.add_facts(facts)
        # If all the facts are duplicates, then return
        if not new_facts:
            return current_leftmost, 0, updated_facts

        new_leftmost = current_leftmost
        logging.debug("%s: Adding to graph, facts: %s", self, new_facts)

        for rule in self.rules:
            when_objs = self._get_matching_objs(rule)
            if when_objs:
                # Get all the permutations associated with the objects
                perms = combinations(when_objs, new_facts)                
                logging.debug("%s: %s, permutations: %s", self, rule, perms)
                # insert to the graph
                for each in perms:
                    node_id = f"{self.id}:{rule.id}:{each}"
                    node = Node(node_id, rule, self, each)
                     # TODO only rule.order based ordering is implemented for now, add other stuff including:
                    # - merge hints
                    # - collection goes after the types it collects
                    # - etc.
                    element = self.graph.add(node, node.rule.order)
                    logging.debug("%s: Added node: %s", self, element)
                    new_leftmost = self._minimum(new_leftmost, element)
        logging.debug("%s: Inserted into graph, count: %d, updated facts: %s, new leftmost: %s", self, len(new_facts), updated_facts, new_leftmost)
        return new_leftmost, new_facts, updated_facts
    
    def _minimum(self, element1:Element, element2:Element)->Element:
        if not element1:
            return element2
        min = element2 if self.graph.compare(element1, element2) >= 0 else element1
        return min
