from .._tpc import _TPC

class TPCH(_TPC):
    """
    TPC-H Benchmark Implementation
    """
    TPC_BENCHMARK_VARIANT = 'H'
    TABLE_REGISTRY = [
        'customer', 'lineitem', 'nation', 'orders', 'part',
        'partsupp', 'region', 'supplier'
    ]
    QUERY_REGISTRY = [
        'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10',
        'q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20',
        'q21', 'q22'
    ]
    DDL_FILE_NAME = 'ddl_v3.0.1.sql'