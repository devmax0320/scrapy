"""
Scheduler disk-based queues
"""

import marshal, cPickle as pickle

from scrapy.utils.queue import DiskQueue


class PickleDiskQueue(DiskQueue):

    def push(self, obj):
        try:
            s = pickle.dumps(obj, protocol=2)
        except pickle.PicklingError, e:
            raise ValueError(str(e))
        super(PickleDiskQueue, self).push(s)

    def pop(self):
        s = super(PickleDiskQueue, self).pop()
        if s:
            return pickle.loads(s)


class MarshalDiskQueue(DiskQueue):

    def push(self, obj):
        super(MarshalDiskQueue, self).push(marshal.dumps(obj))

    def pop(self):
        s = super(MarshalDiskQueue, self).pop()
        if s:
            return marshal.loads(s)
