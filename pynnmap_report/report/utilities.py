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


def build_paired_dataframe(obs_df, prd_df, join_field, attr_field):
    # Ensure we have the columns we want
    assert_columns_in_df(obs_df, (join_field, attr_field))
    assert_columns_in_df(prd_df, (join_field, attr_field))

    # Ensure that all attr_fields values are filled in
    assert_valid_attr_values(obs_df, attr_field)
    assert_valid_attr_values(prd_df, attr_field)

    # Subset down to just the join_field and attr_field
    obs_df = obs_df[[join_field, attr_field]]
    prd_df = prd_df[[join_field, attr_field]]

    # Merge the data frames using an inner join.  Observed column will
    # have an '_O' suffix and predicted column will have a '_P' suffix
    merged_df = obs_df.merge(prd_df, on=join_field, suffixes=('_O', '_P'))

    # Ensure that the length of the merged dataset matches either the
    # original observed or predicted dataframes
    assert_same_len_ids(merged_df, obs_df, prd_df)
    return merged_df


def is_continuous(attr):
    return (
        attr.is_continuous_attr() and
        attr.is_project_attr() and
        attr.is_accuracy_attr() and
        not attr.is_species_attr()
    )


def get_continuous_attrs(mp):
    return [x for x in mp.attributes if is_continuous(x)]
