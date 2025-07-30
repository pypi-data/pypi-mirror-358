
#   Test calling the bnlearn PC-stable structure learning algorithm

import pytest

from core.common import EdgeType
from call.bnlearn import bnlearn_learn
from fileio.common import TESTDATA_DIR
from fileio.numpy import NumPy
from core.bn import BN
import testdata.example_pdags as ex_pdag


@pytest.fixture(scope="module")  # AB, 10 categorical rows
def ab10():
    bn = BN.read(TESTDATA_DIR + '/dsc/ab.dsc')
    return NumPy.from_df(df=bn.generate_cases(10), dstype='categorical',
                         keep_df=False)


def test_bnlearn_gs_type_error_1():  # no arguments
    with pytest.raises(TypeError):
        bnlearn_learn()


def test_bnlearn_gs_type_error_2():  # only one argument
    with pytest.raises(TypeError):
        bnlearn_learn(32.23)
    with pytest.raises(TypeError):
        bnlearn_learn('gs')


def test_bnlearn_gs_type_error_3(ab10):  # bad algorithm type
    with pytest.raises(TypeError):
        bnlearn_learn(True, ab10)
    with pytest.raises(TypeError):
        bnlearn_learn(6, ab10)
    with pytest.raises(TypeError):
        bnlearn_learn(ab10, ab10)


def test_bnlearn_gs_type_error_4(ab10):  # bad data argument type
    with pytest.raises(TypeError):
        bnlearn_learn('gs', 32.23)
    with pytest.raises(TypeError):
        bnlearn_learn('gs', [['A', 'B'], [1, 2]])
    with pytest.raises(TypeError):
        bnlearn_learn('gs', ab10.as_df())


def test_bnlearn_gs_filenotfound_error_1():  # non-existent data file
    with pytest.raises(FileNotFoundError):
        bnlearn_learn('gs', 'nonexistent.txt')


def test_bnlearn_gs_value_error_1(ab10):  # Data has too few columns
    with pytest.raises(ValueError):
        bnlearn_learn('gs', ab10)


def test_bnlearn_gs_value_error_2():  # Data file has too few columns
    with pytest.raises(ValueError):
        bnlearn_learn('gs', TESTDATA_DIR + '/discrete/tiny/ab.dsc')


def test_bnlearn_gs_ab_cb_1k_ok_1():
    data = BN.read(TESTDATA_DIR + '/dsc/ab_cb.dsc').generate_cases(1000)
    data = NumPy.from_df(df=data, dstype='categorical', keep_df=True)
    pdag, _ = bnlearn_learn('gs', data)
    print('\nPDAG learnt by gs from 1K rows of ab_cb:\n{}'.format(pdag))
    assert pdag == ex_pdag.ab_cb()


def test_bnlearn_gs_ab_cb_1k_ok_2():
    data = BN.read(TESTDATA_DIR + '/dsc/ab_cb.dsc').generate_cases(1000)
    data = NumPy.from_df(df=data, dstype='categorical', keep_df=True)
    pdag, _ = bnlearn_learn('gs', data, params={'iss': 10})
    print('\nPDAG learnt by gs from 1K rows of ab_cb:\n{}'.format(pdag))
    assert pdag == ex_pdag.ab_cb()


def test_bnlearn_gs_abc_1k_ok():
    data = BN.read(TESTDATA_DIR +
                   '/discrete/tiny/abc.dsc').generate_cases(1000)
    data = NumPy.from_df(df=data, dstype='categorical', keep_df=True)
    pdag, _ = bnlearn_learn('gs', data)
    print('\nPDAG learnt by gs from 1K rows of abc:\n{}'.format(pdag))
    assert pdag == ex_pdag.abc4()


def test_bnlearn_gs_abc_dual_1k_ok():
    data = BN.read(TESTDATA_DIR +
                   '/discrete/tiny/abc_dual.dsc').generate_cases(1000)
    data = NumPy.from_df(df=data, dstype='categorical', keep_df=True)
    pdag, _ = bnlearn_learn('gs', data)
    print('\nPDAG learnt by gs from 1K rows of abc_dual:\n{}'
          .format(pdag))
    assert pdag == ex_pdag.abc_acyclic4()


def test_bnlearn_gs_and4_10_1k_ok():  # 1->2->4, 3->2, 1K rows
    data = BN.read(TESTDATA_DIR +
                   '/discrete/tiny/and4_10.dsc').generate_cases(1000)
    data = NumPy.from_df(df=data, dstype='categorical', keep_df=True)
    pdag, _ = bnlearn_learn('gs', data)
    print('\nPDAG learnt by gs from 1K rows of and4_10:\n{}'
          .format(pdag))
    print(ex_pdag.and4_11())
    assert pdag.edges == {('X1', 'X2'): EdgeType.UNDIRECTED,
                          ('X2', 'X3'): EdgeType.UNDIRECTED,
                          ('X2', 'X4'): EdgeType.UNDIRECTED}


def test_bnlearn_gs_cancer_1k_ok_1():  # Cancer, 1K rows
    data = NumPy.read(TESTDATA_DIR + '/experiments/datasets/cancer.data.gz',
                      dstype='categorical')
    pdag, _ = bnlearn_learn('gs', data)
    print('\nPDAG learnt by gs from 1K rows of Cancer:\n{}'
          .format(pdag))
    assert pdag.edges == {('Cancer', 'Dyspnoea'): EdgeType.UNDIRECTED,
                          ('Cancer', 'Smoker'): EdgeType.UNDIRECTED,
                          ('Cancer', 'Xray'): EdgeType.UNDIRECTED}


def test_bnlearn_gs_cancer_1k_ok_2():  # Cancer, 1K rows, alpha = 0.001
    data = NumPy.read(TESTDATA_DIR + '/experiments/datasets/cancer.data.gz',
                      dstype='categorical')
    pdag, _ = bnlearn_learn('gs', data, params={'alpha': 0.001})
    print('\nPDAG learnt by gs, 1K rows of Cancer (alpha=0.001):\n{}'
          .format(pdag))
    assert pdag.edges == {('Cancer', 'Smoker'): EdgeType.UNDIRECTED,
                          ('Cancer', 'Xray'): EdgeType.UNDIRECTED}


def test_bnlearn_gs_asia_1k_ok_1():  # Asia, 1K rows
    data = NumPy.read(TESTDATA_DIR + '/experiments/datasets/asia.data.gz',
                      dstype='categorical')
    pdag, _ = bnlearn_learn('gs', data)
    print('\nPDAG learnt by gs from 1K rows of Asia:\n{}'
          .format(pdag))
    assert pdag.edges == {('bronc', 'smoke'): EdgeType.UNDIRECTED,
                          ('bronc', 'dysp'): EdgeType.UNDIRECTED,
                          ('lung', 'either'): EdgeType.DIRECTED,
                          ('tub', 'either'): EdgeType.DIRECTED}


def test_bnlearn_gs_asia_1k_ok_2():  # Asia, 1K rows, alpha=0.01
    data = NumPy.read(TESTDATA_DIR + '/experiments/datasets/asia.data.gz',
                      dstype='categorical')
    pdag, _ = bnlearn_learn('gs', data, params={'alpha': 1E-4})
    print('\nPDAG learnt by gs from 1K rows Asia (alpha=1E-4):\n{}'
          .format(pdag))
    assert pdag.edges == {('bronc', 'smoke'): EdgeType.UNDIRECTED,
                          ('bronc', 'dysp'): EdgeType.UNDIRECTED,
                          ('lung', 'either'): EdgeType.DIRECTED,
                          ('tub', 'either'): EdgeType.DIRECTED}


# Gaussian datasets

def test_bnlearn_gs_gauss_1_ok():  # Gaussian example, 100 rows
    data = NumPy.read(TESTDATA_DIR + '/simple/gauss.data.gz',
                      dstype='continuous', N=100)
    pdag, trace = bnlearn_learn('gs', data, params={'test': 'mi-g'},
                                context={'in': 'in', 'id': 'gauss'})
    print('\nPDAG learnt from 100 rows of gauss: {}\n\n{}'.format(pdag, trace))
    edges = {(e[0], t.value[3], e[1]) for e, t in pdag.edges.items()}
    assert edges == \
        {('C', '->', 'B'),
         ('F', '-', 'G'),
         ('D', '->', 'B')}


def test_bnlearn_gs_gauss_2_ok():  # Gaussian example, 100 rows, rev ord
    data = NumPy.read(TESTDATA_DIR + '/simple/gauss.data.gz',
                      dstype='continuous', N=100)
    data.set_order(tuple(list(data.get_order())[::-1]))
    pdag, trace = bnlearn_learn('gs', data, params={'test': 'mi-g'},
                                context={'in': 'in', 'id': 'gauss'})
    print('\nPDAG learnt from 100 rows of gauss: {}\n\n{}'.format(pdag, trace))
    edges = {(e[0], t.value[3], e[1]) for e, t in pdag.edges.items()}
    assert edges == \
        {('D', '->', 'B'),
         ('G', '->', 'F'),
         ('C', '->', 'B'),
         ('D', '->', 'F')}


def test_bnlearn_gs_gauss_3_ok():  # Gaussian example, 5K rows
    data = NumPy.read(TESTDATA_DIR + '/simple/gauss.data.gz',
                      dstype='continuous')
    pdag, trace = bnlearn_learn('gs', data, params={'test': 'mi-g'},
                                context={'in': 'in', 'id': 'gauss'})
    print('\nPDAG learnt from 5K rows of gauss: {}\n\n{}'.format(pdag, trace))
    edges = {(e[0], t.value[3], e[1]) for e, t in pdag.edges.items()}
    assert edges == \
        {('D', '->', 'F'),
         ('A', '->', 'F'),
         ('B', '-', 'D'),
         ('B', '->', 'C'),
         ('A', '->', 'C'),
         ('E', '->', 'F'),
         ('G', '->', 'F')}


def test_bnlearn_gs_gauss_4_ok():  # Gaussian example, 5K rows, rev ord
    data = NumPy.read(TESTDATA_DIR + '/simple/gauss.data.gz',
                      dstype='continuous')
    data.set_order(tuple(list(data.get_order())[::-1]))
    pdag, trace = bnlearn_learn('gs', data, params={'test': 'mi-g'},
                                context={'in': 'in', 'id': 'gauss'})
    print('\nPDAG learnt from 100 rows of gauss: {}\n\n{}'.format(pdag, trace))
    edges = {(e[0], t.value[3], e[1]) for e, t in pdag.edges.items()}
    assert edges == \
        {('D', '->', 'F'),
         ('A', '->', 'F'),
         ('B', '-', 'D'),
         ('B', '->', 'C'),
         ('A', '->', 'C'),
         ('E', '->', 'F'),
         ('G', '->', 'F')}


def test_bnlearn_gs_sachs_c_1_ok():  # Sachs gauss example, 1K rows
    data = NumPy.read(TESTDATA_DIR + '/experiments/datasets/sachs_c.data.gz',
                      dstype='continuous')
    pdag, trace = bnlearn_learn('gs', data, params={'test': 'mi-g'},
                                context={'in': 'in', 'id': 'gauss'})
    print('\nPDAG rom 1K rows of sachs_c: {}\n\n{}'.format(pdag, trace))
    edges = {(e[0], t.value[3], e[1]) for e, t in pdag.edges.items()}
    print(edges)
    assert edges == \
        {('Mek', '-', 'Raf'),
         ('Jnk', '-', 'PKC'),
         ('Mek', '-', 'PKA'),
         ('PKC', '->', 'P38'),
         ('PIP3', '-', 'Plcg'),
         ('Mek', '-', 'PKC'),
         ('PKA', '->', 'Erk'),
         ('PIP3', '-', 'PKA'),
         ('PKA', '->', 'P38'),
         ('Akt', '->', 'Erk'),
         ('PKC', '-', 'Raf'),
         ('PKA', '-', 'Raf'),
         ('PIP2', '-', 'Plcg'),
         ('PIP2', '-', 'PIP3')}


def test_bnlearn_gs_sachs_c_2_ok():  # Sachs gauss example, rev, 1K rows
    data = NumPy.read(TESTDATA_DIR + '/experiments/datasets/sachs_c.data.gz',
                      dstype='continuous')
    data.set_order(tuple(list(data.get_order())[::-1]))
    pdag, trace = bnlearn_learn('gs', data, params={'test': 'mi-g'},
                                context={'in': 'in', 'id': 'gauss'})
    print('\nPDAG rom 1K rows of sachs_c: {}\n\n{}'.format(pdag, trace))
    edges = {(e[0], t.value[3], e[1]) for e, t in pdag.edges.items()}
    print(edges)
    assert edges == \
        {('Mek', '-', 'Raf'),
         ('Jnk', '-', 'PKC'),
         ('Mek', '-', 'PKA'),
         ('PKC', '->', 'P38'),
         ('PIP3', '-', 'Plcg'),
         ('Mek', '-', 'PKC'),
         ('PKA', '->', 'Erk'),
         ('PIP3', '-', 'PKA'),
         ('PKA', '->', 'P38'),
         ('Akt', '->', 'Erk'),
         ('PKC', '-', 'Raf'),
         ('PKA', '-', 'Raf'),
         ('PIP2', '-', 'Plcg'),
         ('PIP2', '-', 'PIP3')}
