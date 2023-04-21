import os
import gitlab
import logging
import pandas as pd

from functools import cached_property

log = logging.getLogger(__name__)

ACCESS_TOKEN = os.getenv("CI_TOKEN")
gl = gitlab.Gitlab(url="https://gitlab.fixstudio.com/", private_token=ACCESS_TOKEN)
gl.auth()


class Fields:
    """List of all column name of spreadsjeet"""
    EVENT = "Event"
    AUTHOR = "Author"
    TIME_ESTIMATE = "Time estimate"
    TITLE = "Title"
    URL = "Url"
    MOVED_ID = "Moved ID"
    TOTAL_TIME_SPENT = "Time spent (hours)"
    HUMAN_TIME_ESTIMATE = "Time estimate"
    ASSIGNEE_IDS = "Assigne to"
    LABELS_ISSUE = "Labels"
    EPIC = "Epic"
    STATE = "State"
    REPOSITORY = "Repository"
    CREATED_AT = "Created at"
    CLOSED_AT = "Closed at"


class Issue:
    """
        Class returning an object containing all the information of the outcome received by the event

    Attributes:
        _data (dict): Flatten dict contains all the data about one issue
    """
    def __init__(self, data):
        """

        Args:
            data:
        """
        if data:
            try:
                self._data = pd.json_normalize(data, sep='.').to_dict(orient='records')[0]
            except Exception as e:
                log.exception(e)
                self._data = dict()
        else:
            self._data = dict()

    @property
    def is_valid(self):
        return len(self._data) != 0

    @property
    def event_type(self):
        return self._data.get('event_type', "")

    @property
    def project_id(self):
        return self._data.get('project.id', "")

    @property
    def issue_id(self):
        return self._data.get('object_attributes.id', "")

    @property
    def state(self):
        return self._data.get('object_attributes.state', "").upper()

    @property
    def repository(self):
        return self._data.get('repository.name', "")

    @property
    def title(self):
        return self._data.get('object_attributes.title', "")

    @property
    def author(self):
        author_id = self._data.get('object_attributes.author_id', "")
        if author_id:
            author_id = gl.users.get(author_id).name
        return author_id

    @property
    def epic(self):
        project_id = self.project_id
        issue_iid = self._data.get('object_attributes.iid', "")
        epic = ""

        if not project_id or not issue_iid:
            return epic

        try:
            epic = gl.projects.get(project_id).issues.get(issue_iid).epic.get("title")
        except Exception as e:
            pass
        return epic

    @property
    def human_time_estimate(self):
        return self._data.get('object_attributes.human_time_estimate', "")

    @property
    def total_time_spend(self):
        seconds = self._data.get('object_attributes.total_time_spent', "")
        if seconds:
            return round(float(seconds) / 3600.0, 1)
        return seconds

    @property
    def labels_issue(self):
        data_labels = self._data.get('object_attributes.labels', "")
        labels = []
        for label in data_labels:
            labels.append(label['title'])
        return labels

    @property
    def moved_id(self):
        return self._data.get('object_attributes.moved_to_id', "")

    @property
    def url(self):
        return self._data.get('object_attributes.url', "")

    @property
    def assignee_ids(self):
        ids = self._data.get('object_attributes.assignee_ids', "")
        assignee = []
        for id in ids:
            assignee.append(gl.users.get(id).name)
        return assignee

    @property
    def created_at(self):
        created_at = self._data.get('object_attributes.created_at', "")
        if created_at:
            return created_at.split('T')[0]
        return ""

    @property
    def closed_at(self):
        created_at = self._data.get('object_attributes.closed_at', "")
        if created_at:
            return created_at.split('T')[0]
        return ""

    @cached_property
    def dict(self):
        """Construct dict for dataframe"""
        return {
            Fields.EVENT: [self.event_type],
            Fields.REPOSITORY: [self.repository],
            Fields.AUTHOR: [self.author],
            Fields.TITLE: [self.title],
            Fields.URL: [self.url],
            Fields.MOVED_ID: [self.moved_id],
            Fields.ASSIGNEE_IDS: [self.assignee_ids],
            Fields.HUMAN_TIME_ESTIMATE: [self.human_time_estimate],
            Fields.TOTAL_TIME_SPENT: [self.total_time_spend],
            Fields.LABELS_ISSUE: [self.labels_issue],
            Fields.EPIC: [self.epic],
            Fields.STATE: [self.state],
            Fields.CREATED_AT: [self.created_at],
            Fields.CLOSED_AT: [self.closed_at]
        }

    @property
    def dataframe(self):
        dataframe = pd.DataFrame(data=self.dict)
        return dataframe
