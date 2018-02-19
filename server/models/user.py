from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from enum import Enum
from server import Base

class User(Base):
    __tablename__ = 'users'
    id = Column('user_id', Integer, primary_key=True)
    consent = Column('consent', Boolean)
    responses = relationship('Response')
    feedback = Column('feedback', String(250))

    def __repr__(self):
        return '<User {}>\nConsent: {},\nResponses: {},\nFeedback: {}' \
                .format(self.id, self.consent, self.responses, self.feedback)

class VizType(Enum):
    standard = 'standard'
    rollover = 'rollover'
    word2vec = 'word2vec'

class Response(Base):
    __tablename__ = 'responses'
    id = Column('response_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey('users.user_id'))
    theme1 = Column('theme_1', String(120))
    theme1_word1 = Column('theme1_word1', String(120))
    theme1_word2 = Column('theme1_word2', String(120))
    theme1_word3 = Column('theme1_word3', String(120))
    theme2 = Column('theme_2', String(120))
    theme2_word1 = Column('theme2_word1', String(120))
    theme2_word2 = Column('theme2_word2', String(120))
    theme2_word3 = Column('theme2_word3', String(120))
    viz_type = Column('viz_type', String(50))
    start_time = Column('start_time', String(50))
    end_time = Column('end_time', String(50))

    def __repr__(self):
        return '<Response {}>\nUser:{},\nTheme 1: {},\nTheme 2: {},\nViz. Type: {},\nStart: {},\nEnd:{}' \
                .format(self.id, self.parent_id, self.theme1, self.theme2, self.viz_type,
                        self.start_time, self.end_time)
