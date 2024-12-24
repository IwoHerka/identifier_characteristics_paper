# Existing imports and code...

class Function(Base):
    __tablename__ = "functions"

    # Existing columns...

    # Add new columns for identifier metrics
    median_id_length = Column(Float, nullable=True)
    median_id_syllable_count = Column(Float, nullable=True)
    median_id_soft_word_count = Column(Float, nullable=True)
    id_duplicate_percentage = Column(Float, nullable=True)
    num_single_letter_ids = Column(Float, nullable=True)
    id_most_common_casing_style = Column(Float, nullable=True)
    id_percent_abbreviations = Column(Float, nullable=True)
    id_percent_dictionary_words = Column(Float, nullable=True)
    median_id_lv_dist = Column(Float, nullable=True)
    num_consistency_violations = Column(Float, nullable=True)
    num_conciseness_violations = Column(Float, nullable=True)

    # Rest of the existing code... 