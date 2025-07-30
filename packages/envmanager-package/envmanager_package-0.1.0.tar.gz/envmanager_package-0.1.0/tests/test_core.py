import os
import tempfile
import pytest
from envmanager.core import EnvManager

def test_add_and_remove():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        env_path = tf.name
    try:
        manager = EnvManager(env_path)
        manager.add('FOO', 'bar')
        manager.load()
        assert manager.env['FOO'] == 'bar'
        manager.remove('FOO')
        manager.load()
        assert 'FOO' not in manager.env
    finally:
        os.remove(env_path)

def test_validate():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        env_path = tf.name
    try:
        manager = EnvManager(env_path)
        manager.add('A', '1')
        manager.add('B', '2')
        missing = manager.validate(['A', 'B', 'C'])
        assert missing == ['C']
    finally:
        os.remove(env_path)

def test_generate_from_template():
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tf:
        tf.write('X=1\nY=2\n')
        template_path = tf.name
    with tempfile.NamedTemporaryFile(delete=False) as tf2:
        env_path = tf2.name
    try:
        manager = EnvManager(env_path)
        manager.generate_from_template(template_path)
        manager.load()
        assert manager.env['X'] == '1'
        assert manager.env['Y'] == '2'
    finally:
        os.remove(template_path)
        os.remove(env_path) 