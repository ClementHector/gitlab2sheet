import logging
import pandas as pd
import numpy as np
import pygsheets
import os

from src.issue import Issue, Fields

path_to_current_file = os.path.realpath(__file__)
current_directory = os.path.split(path_to_current_file)[0]

log = logging.getLogger(__name__)


def url_exists(target_url, urls):
    """
    Checks if a target URL exists in a list of URLs.

    Parameters:
        target_url (str): URL to search for.
        urls (List[str]): List of URLs to search in.

    Returns:
        bool: True if the target URL exists in the list of URLs, False otherwise.
    """
    for url in urls:
        if url == target_url:
            return True
    return False


class SpreadsheetController:
    """
    A class allowing to handle updating Google Sheets with data from a Pandas DataFrame.
    """

    def __init__(self, data=None):
        """
        Initializes the Spreadsheet object.

        Args:
            data (dict): Dictionary containing the data for the issue.

        Attributes:
            self._gc (pygsheets.client.Client): Authorized client for interacting with Google Sheets API.
            self._spreadsheet (pygsheets.Spreadsheet): Spreadsheet object.
            self.issue (Issue): Issue object.
        """

        if data is None:
            data = {}
        log.debug("Init SpreadsheetController class with data: {}".format(data))
        self._gc = pygsheets.authorize(service_account_file=os.path.join(
            current_directory, '../cred/gitlab-371919-efb61b5ab920.json'))
        self._spreadsheet = None
        self.issue = Issue(data)

    def open(self, title="test-gitlab"):
        """
        Opens a spreadsheet in Google Sheets by its title.

        Args:
            title (str): Title of the spreadsheet to open. Default value is "Issue logs".

        Returns:
            bool: If the spreadsheet was found and opened successfully, the function returns True. If the spreadsheet
                  was not found, the function returns False.

        Raises:
            pygsheets.SpreadsheetNotFound: This exception is raised if the spreadsheet was not found.

        Example:
            spreadsheet = Spreadsheet(data)
            if spreadsheet.open("My Spreadsheet"):
                # The spreadsheet was opened successfully
            else:
                # The spreadsheet was not found
        """
        try:
            self._spreadsheet = self._gc.open(title)
            log.debug("Spreadsheet {} opened.".format(title))
        except pygsheets.SpreadsheetNotFound:
            log.exception("Spreadsheet titled {} not found.".format(title))
            return False
        return True

    def get_dataframe(self):
        """Return current dataframe of first worksheet"""
        worksheet = self._spreadsheet.worksheet()
        return worksheet.get_as_df()

    def update(self):
        """
            Update of the spreadsheet with the insertion of the outcome data from issue event

        Returns:
            bool: True if the spreadsheet is update, otherwise, False
        """
        if not self._spreadsheet:
            log.error("Spreadsheet need to be open before update")
            return False
        if not self.issue.is_valid:
            log.error("Something is wrong with the issue, check the consistency of data received")
            return False
        try:
            # Get the first worksheet of spreadsheet
            worksheet = self._spreadsheet.worksheet()
            log.debug("Worksheet {} opened.".format(worksheet))

            # Get all values from spreadsheet on DataFrame
            dataframe = worksheet.get_as_df()
            log.debug("Actual dataframe: {}".format(dataframe))

            # If the issue URL does not exist in the spreadsheet, we simply concatenate the received data to the
            # existing ones, otherwise, we replace the values of the issue
            if not url_exists(self.issue.url, dataframe.get(Fields.URL, [])):
                dataframe = pd.concat([dataframe, self.issue.dataframe])
            else:
                # Get the row index of specific issue
                issue_index = dataframe.index[(dataframe[Fields.URL] == self.issue.url)].tolist()
                log.debug("Issue index: {}".format(issue_index))

                # Replace old outcome data with new data
                df_cols = list(dataframe.columns)
                issue_df_cols = self.issue.dataframe.columns.tolist()
                dataframe.loc[issue_index, df_cols] = self.issue.dataframe[issue_df_cols].values

            # Replace None and NaN value from dataframe by empty string
            dataframe.replace(['None', np.nan], "", inplace=True)
            log.debug("Dataframe updated: {}".format(dataframe))
            worksheet.set_dataframe(dataframe, (1, 1))
        except Exception as e:
            log.exception(e)
            return False
        return True
