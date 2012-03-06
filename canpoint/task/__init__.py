# -*- coding: utf-8 -*-

"""
    task
    ~~~~~~~~~~~~

    task management.
"""

import os
from multiprocessing import Pool, Process, Queue, Manager, Value
from formcapture import generate_capture

import logging, traceback
logger = logging.getLogger(__name__)

IS_WINDOWS = (os.name == 'nt')

def pth(fname):
    return os.path.abspath(os.path.join('.', fname))


class BaseManager:
    def __init__(self):
        self.tasks = Queue()
        self.task_count = 0
        self.done_task_count = Value('i', 0)
        self.log_path = pth('task_debug.log')

    def add_task(self, task):
        logger.debug(';'.join([t for t in task]))
        self.tasks.put(task)
        self.task_count += 1

    def has_finished(self):
        return self.task_count == self.done_task_count.value

    def get_status(self):
        return self.task_count, self.done_task_count.value

    def start(self):
        self.proc = Process(target=self.serve, args=(self.tasks, self.done_task_count, self.log_path))
        self.proc.daemon = True
        self.proc.start()

    def serve(self, tasks, done_count, log_path):
        import logging
        logging.basicConfig(filename=log_path, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

        while True:
            try:
                task = tasks.get()
                self._process(task)
                # FIXME: task_done is available only in JoinableQueue
                #tasks.task_done()
            except:
                logger = logging.getLogger(__name__)
                logger.debug(traceback.format_exc())
            finally:
                done_count.value += 1
 
    def _process(self, task):
        pass


class FormCaptureManager(BaseManager):
    def __init__(self):
        BaseManager.__init__(self)
        if IS_WINDOWS:
            self.exepath = pth('tools', 'cutycapt.exe')
        else:
            self.exepath = pth('tools', 'cutycapt')
            #self.exepath = 'webkit-image-qt'

    def _process(self, task):
        generate_capture(self.exepath, *task)

