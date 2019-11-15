import pandas as pd


def is_continuous(attr):
    return (
        attr.is_continuous_attr() and
        attr.is_project_attr() and
        attr.is_accuracy_attr() and
        not attr.is_species_attr()
    )


def get_continuous_attrs(mp):
    return [x for x in mp.attributes if is_continuous(x)]


def assert_columns_in_df(df, cols):
    try:
        assert(set(cols).issubset(df.columns))
    except AssertionError:
        msg = 'Columns do not appear in dataframe'
        raise NameError(msg)


def assert_valid_attr_values(df, attr):
    try:
        assert df[attr].isnull().sum() == 0
    except AssertionError:
        msg = 'Data frame has null attribute values'
        raise ValueError(msg)


def assert_same_len_ids(merged_df, df1, df2):
    try:
        merge_num = len(merged_df)
        assert(merge_num == len(df1) or merge_num == len(df2))
    except AssertionError:
        msg = 'Merged data frame does not have same length as originals'
        raise ValueError(msg)


def _list_like(x):
    return x if type(x) in [list, tuple] else [x]


def build_paired_dataframe(obs_df, prd_df, join_field, attr_fields):
    # Ensure we have the columns we want
    attr_fields = _list_like(attr_fields)
    columns = [join_field] + _list_like(attr_fields)
    assert_columns_in_df(obs_df, columns)
    assert_columns_in_df(prd_df, columns)

    # Ensure that all attr_fields values are filled in
    for attr_field in attr_fields:
        assert_valid_attr_values(obs_df, attr_field)
        assert_valid_attr_values(prd_df, attr_field)

    # Subset down to just the columns
    obs_df = obs_df[columns]
    prd_df = prd_df[columns]

    # Merge the data frames using an inner join.  Observed column will
    # have an '_O' suffix and predicted column will have a '_P' suffix
    merged_df = obs_df.merge(prd_df, on=join_field, suffixes=('_O', '_P'))

    # Ensure that the length of the merged dataset matches either the
    # original observed or predicted dataframes
    assert_same_len_ids(merged_df, obs_df, prd_df)
    return merged_df


def build_paired_dataframe_from_files(obs_fn, prd_fn, join_field, attr_fields):
    columns = [join_field] + _list_like(attr_fields)
    obs_df = pd.read_csv(obs_fn, usecols=columns)
    prd_df = pd.read_csv(prd_fn, usecols=columns)
    return build_paired_dataframe(obs_df, prd_df, join_field, attr_fields)
