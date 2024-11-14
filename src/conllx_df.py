import re
from typing import List, Union

import pandas as pd
from pandas import DataFrame
    
class ConllxDf:
    def __init__(self, file_path='', data=None):
        self.file_path = file_path
        self.data = data
        if not data:
            with open(self. file_path, 'r') as f:
                self.data = ''.join(f.readlines())
        # remove special character \ufeff, if file starts with it (it causes errors)
        self.data: str = self.data.replace('\ufeff', '')

        self._df: DataFrame = self.__init_conllx_df()
        self._comments: List[List[str]] = self.__init_list_of_comments()
        
    @staticmethod
    def get_conllu_header() -> List[str]:
        """return the column headers based on CoNLL-U.

        Returns:
            List[str]: a list of column names
        """
        return ['ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
    
    def __init_conllx_df(self) -> DataFrame:
        """Initializes the class variable df as a DataFrame of all trees.

        Returns:
            DataFrame: the given conll file trees
        """
        # get non-comment lines (ignores empty lines)
        matcher = re.compile(r'^(?!#).+$', re.MULTILINE)
        conll_rows: List[str] = matcher.findall(self.data)
        
        # initialize DataFrame. Rows are placed in a single column (0), split column on \t
        df = DataFrame(conll_rows)
        df = df[0].str.split('\t',expand=True)
        
        # df now has 10 columns, name them (we assume the headers follow CoNLL-U)
        df.columns = self.get_conllu_header()
        # child and parent IDs are ints
        df[['ID', 'HEAD']] = df[['ID', 'HEAD']].apply(pd.to_numeric)
        return df
    
    def __init_list_of_comments(self) -> List[List[str]]:
        """Initializes the class variable comments as a list of lists of comments.
        Within the comments list:
        Each list represents the comments of the given tree.
        
        An empty list represents a tree with no comments.

        Returns:
            List[List[str]]: a list of lists of comments
        """
        # get lines starting with # and blank lines
        # the blank lines represent the end of the tree/tree comments.
        matcher = re.compile(r'^(\s*|#.*)$', re.MULTILINE)
        
        # a flat list of all comments
        lines: List[str] = matcher.findall(self.data)
        
        # create a list of lists of comments
        final_list: List[List[str]] = []
        temp_list: List[str] = []
        for line in lines:
            if line == '': # an empty string represents the end of comments of the given tree.
                final_list.append(temp_list)
                temp_list = []
            else:
                temp_list.append(line)
        return final_list
    
    # TODO
    # def write(self):
        # update self.data using df and comments
        
    
    def get_df_by_id(self, df_number: int) -> Union[DataFrame, None]:
        """Given a tree number, return the corresponding df.
        The number must be between [0,len(conllx_df)), otherwise None is returned.

        Note: the tree is extracted from a DataFrame containing all trees,
        and so the index column will contain a range with respect to
        the full DataFrame. The index column is not related to the tree data.
        
        Args:
            df_number (int): tree number

        Returns:
            Union[DataFrame, None]: a DataFrame or None.
        """
        
        # get starting point for each df
        ids = self.df[self.df['ID'] == 1].index
        # invalid df_number i.e. larger than current list, or negative?
        if df_number >= len(ids) or df_number < 0:
            return None
        # last df
        if df_number == len(ids) - 1:
            return self.df.loc[ids[df_number]:self.df.tail(1).index[0]]
        # remaining df's
        return self.df.loc[ids[df_number]:(ids[df_number+1]-1)]
    
    def get_sentence_count(self):
        return self.df[self.df['ID'] == 1].index.shape[0]
    
    def get_texts(self) -> List[str]:
        return [s[0].split(" = ")[1] for s in self.comments]
    
    def get_texts_tokens(self) -> List[str]:
        return [s[1].split(" = ")[1] for s in self.comments]
    
    @property
    def df(self) -> DataFrame:
        return self._df
    
    @property
    def comments(self) -> List[List[str]]:
        return self._comments
