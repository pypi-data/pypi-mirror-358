import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class FileTools:

    def __init__(self, filepath : str):
        self.filepath= filepath
        root, self.ext = os.path.splitext(filepath)
        
    def read(self):
        if self.ext == '.txt':
            return self._read_txt()
        elif self.ext == '.xlsx':
            return self._read_excel()
        else:
            raise ValueError('File Not Supported, support only .txt and .xlsx')
        
    def _read_txt(self):
        try:
            df= pd.read_csv(self.filepath, sep='\t', keep_default_na=False, na_values='', dtype=str, encoding='iso-8859-1')
            logger.info('File readed Succesfuly')
            return df
        except Exception as e:
            logger.error(f'Error While Reading the file txt.\n{e}', exc_info=True)
            raise
    
    def _read_excel(self):
        try:
            df= pd.read_excel(self.filepath,keep_default_na=False, na_values='', dtype=str)
            logger.info('File readed Succesfuly')
            return df
        except Exception as e:
            logger.error(f'Error While Reading the file txt.\n{e}', exc_info=True)
            raise

    def export_to_txt(self, file: pd.DataFrame):     
        try:
            file.to_csv(self.filepath.replace(self.ext, "_output.txt"), index=False, sep='\t')
            logger.info("Data exported successfully.")
        except PermissionError as e:
            logger.error(f"Permission error while exporting to Excel: {e}", exc_info=True)
            file.to_csv(self.filepath.replace(self.ext, "_output1.txt"), index=False, sep='\t')
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}", exc_info=True)
            raise

    def expand_extracted_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Expands the 'Extracted_Data' column into 'PARTS' and 'TEMPS'.

        Args:
            df (pd.DataFrame): DataFrame containing 'Extracted_Data'.

        Returns:
            pd.DataFrame: Expanded DataFrame.
        """
        logger.info("Expanding 'Extracted_Data' column into parts and temps.")
        try:
            # Only apply on non-null dicts
            df['Extracted_Data'] = df['Extracted_Data'].apply(
                lambda x: list(x.items()) if isinstance(x, dict) else x
            )

            exploded_df = df.explode("Extracted_Data", ignore_index=True)
            exploded_df[['PARTS', 'TEMPS']] = pd.DataFrame(
                exploded_df['Extracted_Data'].apply(
                    lambda x: [None, None] if pd.isna(x) else (x[0], x[1])
                ).tolist(), columns=['PARTS', 'TEMPS']
            )
            exploded_df.drop(columns='Extracted_Data', inplace=True)
            return exploded_df
        except Exception as e:
            logger.error(f"Error expanding data: {e}", exc_info=True)
            raise


