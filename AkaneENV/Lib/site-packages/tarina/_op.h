#pragma once

#include <Python.h>

#ifndef LINEAR_PROBES
#define LINEAR_PROBES 9
#endif

/* This must be >= 1 */
#define PERTURB_SHIFT 5

static inline Py_ssize_t tuplesize(PyObject *ob) {
    PyVarObject *var_ob = (PyVarObject*)ob;
    return var_ob->ob_size;
}

static inline PyObject * tupleitem(PyObject *a, Py_ssize_t i)
{
    return ((PyTupleObject*)a)->ob_item[i];
}


static int contains(PyObject *chs, Py_UCS4 ch) {
    Py_ssize_t i = 0;
    Py_ssize_t length = tuplesize(chs);
    while (1) {
        if (i >= length) {
            return 0;
        }
        if (ch == PyUnicode_READ_CHAR(tupleitem(chs, i), 0)) {
            return 1;
        }
        i++;
    }
    return 0;
}


static setentry *
set_lookkey(PySetObject *so, PyObject *key, Py_hash_t hash)
{
    setentry *table;
    setentry *entry;
    size_t perturb = hash;
    size_t mask = so->mask;
    size_t i = (size_t)hash & mask; /* Unsigned for defined overflow behavior */
    int probes;
    int cmp;

    while (1) {
        entry = &so->table[i];
        probes = (i + LINEAR_PROBES <= mask) ? LINEAR_PROBES: 0;
        do {
            if (entry->hash == 0 && entry->key == NULL)
                return entry;
            if (entry->hash == hash) {
                PyObject *startkey = entry->key;
                assert(startkey != dummy);
                if (startkey == key)
                    return entry;
                if (PyUnicode_CheckExact(startkey)
                    && PyUnicode_CheckExact(key)
                    && _PyUnicode_EQ(startkey, key))
                    return entry;
                table = so->table;
                Py_INCREF(startkey);
                cmp = PyObject_RichCompareBool(startkey, key, Py_EQ);
                Py_DECREF(startkey);
                if (cmp < 0)
                    return NULL;
                if (table != so->table || entry->key != startkey)
                    return set_lookkey(so, key, hash);
                if (cmp > 0)
                    return entry;
                mask = so->mask;
            }
            entry++;
        } while (probes--);
        perturb >>= PERTURB_SHIFT;
        i = (i * 5 + 1 + perturb) & mask;
    }
}


static int
set_contains_key(PyObject *so, PyObject *key)
{
    Py_hash_t hash;
    setentry *entry;

    if (!PyUnicode_CheckExact(key) ||
        (hash = ((PyASCIIObject *)key)->hash) == -1) {
        hash = PyObject_Hash(key);
        if (hash == -1)
            return -1;
    }

    entry = set_lookkey(((PySetObject *)so), key, hash);
    if (entry != NULL)
        return entry->key != NULL;
    return -1;
}