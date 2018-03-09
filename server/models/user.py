from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from enum import Enum
from server import Base

class VizType(Enum):
    standard = 'standard'
    rollover = 'rollover'
    word2vec = 'word2vec'

class User(Base):
    __tablename__ = 'users'
    id = Column('user_id', Integer, primary_key=True)
    cookie = Column('cookie', String(250))
    ip_address = Column('ip_address', String(250))
    viz_type = Column('viz_type', String(50))
    theme1 = Column('theme_1', String(120))
    theme1_word1 = Column('theme1_word1', String(120))
    theme1_word2 = Column('theme1_word2', String(120))
    theme1_word3 = Column('theme1_word3', String(120))
    theme2 = Column('theme_2', String(120))
    theme2_word1 = Column('theme2_word1', String(120))
    theme2_word2 = Column('theme2_word2', String(120))
    theme2_word3 = Column('theme2_word3', String(120))
    start_time = Column('start_time', String(50))
    end_time = Column('end_time', String(50))
    feedback = Column('feedback', String(1500))

    def __repr__(self):
        return '<User {}>\nConsent: {},\nResponses: {},\nFeedback: {}' \
                .format(self.id, self.consent, self.responses, self.feedback)
