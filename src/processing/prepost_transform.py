import pandas as pd

def prepost_transform(data):
    # Transform pre-test results
    pretest_df = data[data['test_type'] == 'pre-test'].copy()

    pretest_df.drop(
        columns=['zip_code', 'test_type', 'years_at_camp'],
        inplace=True)

    pretest_df = pretest_df.melt(
        id_vars=pretest_df.iloc[:, 0:5].columns,
        var_name='question',
        value_name='score_pretest')

    # Transform post-test results
    posttest_df = data[data['test_type'] == 'post-test'].copy()

    posttest_df.drop(
        columns=['zip_code', 'test_type', 'years_at_camp'],
        inplace=True)

    posttest_df = posttest_df.melt(
        id_vars=posttest_df.iloc[:, 0:5].columns,
        var_name='question',
        value_name='score_posttest')

    # Combine the melted pre and post test data
    data = pretest_df.merge(
        posttest_df[['client', 'question', 'score_posttest']],
        on=['client', 'question'],
        how='inner'
    )

    # Calculated the delta between pre-test and post-test scores
    data['delta'] = data['score_posttest'] - data['score_pretest']

    # Strip the question text from the quesion number
    data['question'] = data['question'].str.split('.').str[0]
    
    return data