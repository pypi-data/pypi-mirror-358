from time import time
import traceback

def timestamp():
    return int(round(time() * 1000))

def trace(filter=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            from knowledgenet.service import trace_buffer
            buffer = trace_buffer.get()
            
            filter_pass = filter(args, kwargs) if filter else True
            to_trace = buffer is not None and filter_pass
            if to_trace:
                # TODO: This is a nice trace, but a big memory hog. Devise another type of tracing where the trace is streamed as each of the @trace() calls are done            
                class_name = f"{args[0].__class__.__module__}.{args[0].__class__.__name__}" if args else 'Unknown'
                object_id = getattr(args[0], 'id', 'unknown')
                func_name = func.__name__
                trace = {'obj': f"{object_id}",
                    'func': f"{class_name}.{func_name}",
                    'args': [f"{arg}" for arg in args],
                    'kwargs': kwargs,
                    'start': timestamp(),
                    'calls': []
                }
                trace_buffer.set(trace['calls'])
            ret = None
            exception_trace = None
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                if to_trace:
                    exception_trace = traceback.format_exc()
                raise e
            finally:
                if to_trace:
                    trace['end'] = timestamp()
                    trace['ret'] = f"{ret}"
                    if exception_trace:
                        trace['exc'] = exception_trace
                    buffer.append(trace)
                    trace_buffer.set(buffer)
            return ret
        wrapper.__wrapped__ = True
        return wrapper
    decorator.__wrapped__ = True
    return decorator
