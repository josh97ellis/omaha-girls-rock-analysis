import pandas as pd
import os


os.chdir('C:/Users/Josh Ellis/OneDrive - University of Nebraska at Omaha/' +
         'COURSES/FALL_2022/ISQA8156-820/course-project')


def import_data():
    pretest_older_2018 = (
        pd.read_excel(
            'data/raw/2018Girls Rock Data Analysis.xlsx',
            sheet_name='PREtest-Older Group',
            skiprows=1))
    pretest_older_2018['age_group'] = 'older group'
    pretest_older_2018['year'] = '2018'
    pretest_older_2018['test_type'] = 'pre-test'

    posttest_older_2018 = (
        pd.read_excel(
            'data/raw/2018Girls Rock Data Analysis.xlsx',
            sheet_name='POSTtest-Older Group',
            skiprows=1))
    posttest_older_2018['age_group'] = 'older group'
    posttest_older_2018['year'] = '2018'
    posttest_older_2018['test_type'] = 'post-test'

    pretest_younger_2018 = (
        pd.read_excel(
            'data/raw/2018Girls Rock Data Analysis.xlsx',
            sheet_name='PREtest-Younger Group',
            skiprows=1))
    pretest_younger_2018['age_group'] = 'younger group'
    pretest_younger_2018['year'] = '2018'
    pretest_younger_2018['test_type'] = 'pre-test'

    posttest_younger_2018 = (
        pd.read_excel(
            'data/raw/2018Girls Rock Data Analysis.xlsx',
            sheet_name='POSTtest-Older Group',
            skiprows=1))
    posttest_younger_2018['age_group'] = 'younger group'
    posttest_younger_2018['year'] = '2018'
    posttest_younger_2018['test_type'] = 'post-test'

    pretest_older_2019 = (
        pd.read_excel(
            'data/raw/2019Girls Rock Data Analysis.xlsx',
            sheet_name='PREtest-Older Group',
            skiprows=1))
    pretest_older_2019['age_group'] = 'older group'
    pretest_older_2019['year'] = '2019'
    pretest_older_2019['test_type'] = 'pre-test'

    posttest_older_2019 = (
        pd.read_excel(
            'data/raw/2019Girls Rock Data Analysis.xlsx',
            sheet_name='POSTtest-Older Group',
            skiprows=1))
    posttest_older_2019['age_group'] = 'older group'
    posttest_older_2019['year'] = '2019'
    posttest_older_2019['test_type'] = 'post-test'

    pretest_younger_2019 = (
        pd.read_excel(
            'data/raw/2019Girls Rock Data Analysis.xlsx',
            sheet_name='PREtest-Younger Group',
            skiprows=1))
    pretest_younger_2019['age_group'] = 'younger group'
    pretest_younger_2019['year'] = '2019'
    pretest_younger_2019['test_type'] = 'pre-test'

    posttest_younger_2019 = (
        pd.read_excel(
            'data/raw/2019Girls Rock Data Analysis.xlsx',
            sheet_name='POSTtest-Younger Group',
            skiprows=1))
    posttest_younger_2019['age_group'] = 'younger group'
    posttest_younger_2019['year'] = '2019'
    posttest_younger_2019['test_type'] = 'post-test'

    return (
        pretest_older_2018,
        posttest_older_2018,
        pretest_younger_2018,
        posttest_younger_2018,
        pretest_older_2019,
        posttest_older_2019,
        pretest_younger_2019,
        posttest_younger_2019
    )


def create_id(df):
    df_2018 = df[df['year'] == '2018'].copy()
    df_2019 = df[df['year'] == '2019'].copy()

    d=dict((i,int(j)+1) for j,i in enumerate(df_2018['Client ID'].unique()))
    df_2018.replace({'Client ID': d}, inplace=True)
    df = pd.concat([df_2018, df_2019])
    df['Client ID'] = df['Client ID'].astype(str) + df['Zip Code'].astype(str).str.split('.').str[0] + df['year'].astype(str)
    return df


def remove_columns(df):
    df = df.iloc[:, 0:37]
    for col in df.iloc[:, 5:19].columns:
        df.drop(columns=[col], inplace=True)
    df.drop(columns=df.iloc[:, -4:-3], inplace=True)
    return df


def rename_columns(df):
    # Rename and Standarize Column Headers
    df.rename(
        columns={
            'Client ID': 'client',
            'Age': 'age',
            'Years at Camp': 'years_at_camp',
            'Race/Ethnicity': 'race/ethnicity',
            'Zip Code': 'zip_code'},
        inplace=True)
    return df


def clean_data(df):
    # Convert Zip to string type
    df['zip_code'] = (
        df['zip_code']
        .astype(str)
        .str.split('.').str[0])

    # Trim and convert years_at_camp field to int type
    df['years_at_camp'] = (
        df['years_at_camp']
        .astype(str)
        .str.rstrip('nd|th|st|rd')
        .astype(int))

    # Standardize the race field
    df['race/ethnicity'] = df['race/ethnicity'].str.lower()
    df['race/ethnicity'] = (
        df['race/ethnicity']
        .str.replace(', ', '/')
        .str.replace(' / ', '/')
        .str.replace(' /', '/')
        .str.replace('black/african', 'black')
        .str.replace('hispanic/latinx', 'hispanic')
        .str.replace('hispanic latinx', 'hispanic')
        .str.replace('korean', 'asian')
        .str.replace('asian/caucasian', 'caucasian/asian')
    )

    def race_grouping(df):
        if df['race/ethnicity'] == 'caucasian':
            return 'caucasian'
        elif df['race/ethnicity'] == 'black':
            return 'black'
        elif "/" in str(df['race/ethnicity']):
            return 'multi-racial'
        else:
            return 'other'

    df['race/ethnicity'] = df.apply(race_grouping, axis=1)

    # Enumerate the scaling for the last three questions
    score_dict = {
        'strongly disagree': 6,
        'disagree': 5,
        'somewhat disagree': 4,
        'somewhat agree': 3,
        'agree': 2,
        'strongly agree': 1,
    }

    for col in df.iloc[:, -6:-3].columns:
        df[col] = df[col].str.lower()
        df.replace({col: score_dict}, inplace=True)

    # Replace missing values with the median answer score
    for col in df.iloc[:, 5:19].columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Move last 3 columns to front
    start_idx = 0
    for column in df.iloc[:, -3:].columns:
        col = df.pop(column)
        df.insert(start_idx, col.name, col)
        start_idx += 1
    
    # Move client id to front
    first_column = df.pop('client')
    df.insert(0, 'client', first_column)

    return df


def load_data(df):
    df.to_csv(
        'data/processed/girls_rock_data.csv',
        index=False)


def main():
    data = pd.concat(import_data())
    data = create_id(data)
    data = remove_columns(data)
    data = rename_columns(data)
    data = clean_data(data)
    load_data(data)


if __name__ == '__main__':
    main()
