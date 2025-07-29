"""
Script for storing run data to a sqlite db.

TODO: Allow deletion of items by name
"""

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class LexicalMetricsScores(Base):
    __tablename__ = "lexical_metrics_scores"

    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    question_path = Column(String)
    exact_match_score = Column(Float)
    f1_score = Column(Float)
    rouge_1_score = Column(Float)
    rouge_2_score = Column(Float)
    rouge_l_score = Column(Float)
    exact_match_by_question = Column(JSON)
    f1_score_by_question = Column(JSON)
    rouge_1_by_question = Column(JSON)
    rouge_2_by_question = Column(JSON)
    rouge_l_by_question = Column(JSON)
    date_time = Column(DateTime, default=func.now())


class SemanticSimilarityScores(Base):
    __tablename__ = "semanticSimilarity_metrics_scores"

    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    question_path = Column(String)
    semanticSimilarity_score = Column(Float)
    semanticSimilarity_score_by_question = Column(JSON)
    date_time = Column(DateTime, default=func.now())


class answerCorrectScores(Base):
    __tablename__ = "answerCorrect_metrics_scores"

    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    question_path = Column(String)
    answerCorrect_score = Column(Float)
    answerCorrect_score_by_question = Column(JSON)
    date_time = Column(DateTime, default=func.now())


class DocumentMatchScores(Base):
    __tablename__ = "DocumentMatch_metrics_scores"

    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    question_path = Column(String)
    MeanDocumentMatch_score = Column(Float)
    WeightedDocumentMatch_score = Column(JSON)
    date_time = Column(DateTime, default=func.now())


def save_benchmark_results(model_name, db_name: str, question_path, scores: dict, connection_string: str = None):
    """Save benchmarking results to a database."""

    if connection_string is None:
        db_path = os.path.join(os.getcwd(), db_name)
        engine = create_engine(f"sqlite:///{db_path}")
    else:
        engine = create_engine(connection_string)

    Base.metadata.create_all(engine)
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        for test, scoring in scores.items():
            if test == "LexicalMetrics":
                lexical_run = LexicalMetricsScores(
                    model_name=model_name,
                    question_path=str(question_path),
                    exact_match_score=float(scoring["exact_match_score"].iloc[0]),
                    f1_score=float(scoring["f1_score"].iloc[0]),
                    rouge_1_score=float(scoring["rouge_1_score"].iloc[0]),
                    rouge_2_score=float(scoring["rouge_2_score"].iloc[0]),
                    rouge_l_score=float(scoring["rouge_l_score"].iloc[0]),
                    exact_match_by_question=scoring["exact_match_by_question"].to_json(),
                    f1_score_by_question=scoring["f1_score_by_question"].to_json(),
                    rouge_1_by_question=scoring["rouge_1_by_question"].to_json(),
                    rouge_2_by_question=scoring["rouge_2_by_question"].to_json(),
                    rouge_l_by_question=scoring["rouge_l_by_question"].to_json(),
                )
                session.add(lexical_run)
                print(f"Added LexicalMetrics results to table {LexicalMetricsScores.__tablename__}")

            elif test == "SemanticSimilarity":
                semanticSimilarity_run = SemanticSimilarityScores(
                    model_name=model_name,
                    question_path=str(question_path),
                    semanticSimilarity_score=float(scoring["answerSimilarity_score"].iloc[0]),
                    semanticSimilarity_score_by_question=scoring["answerSimilarity_score_by_question"].to_json(),
                )
                session.add(semanticSimilarity_run)
                print(f"Added SemanticSimilarityScores results to table {SemanticSimilarityScores.__tablename__}")
            elif test == "AnswerCorrect":
                answerCorrect_run = answerCorrectScores(
                    model_name=model_name,
                    question_path=str(question_path),
                    answerCorrect_score=float(scoring["answerCorrect_score"].iloc[0]),
                    answerCorrect_score_by_question=scoring["answerCorrect_score_by_question"].to_json(),
                )
                session.add(answerCorrect_run)
                print(f"Added SemanticSimilarityScores results to table {SemanticSimilarityScores.__tablename__}")

            elif test == "DocumentMatch":
                documentMatch_run = DocumentMatchScores(
                    model_name=model_name,
                    question_path=str(question_path),
                    MeanDocumentMatch_score=float(scoring["MeanDocumentMatch"].iloc[0]),
                    WeightedDocumentMatch_score=float(scoring["WeightedDocumentMatch"].iloc[0]),
                )
                session.add(documentMatch_run)
                print(f"Added DocumentMatch scores results to table {DocumentMatchScores.__tablename__}")
        session.commit()
    except Exception as e:
        print(f"Error saving metrics: {e}")
        raise
    finally:
        engine.dispose()


def fetch_metrics_results(db_name: str | Path = "benchmark.db", connection_string: str = None) -> pd.DataFrame:
    """Fetch metrics results from the database for previous runs and return
    them as a pandas DataFrame.

    :param db_name: Same path used to create the database - if str - path joined from os.getcwd(), the current
    working directory, if path - resolves path and joined from os.getcwd()
    :param connection_string: If you want to connect to an external postgres instance instead of local SQLlite

    :returns:
    pd.DataFrame: Important results from benchmark test combined on model name
    """

    if connection_string is None:
        # Initialize the database engine and session
        if isinstance(db_name, str):
            db_path = os.path.join(os.getcwd(), db_name)
        elif isinstance(db_name, Path):
            db_path = os.path.join(os.getcwd(), db_name.resolve())
        else:
            raise ValueError("db_name must be either a str or Path")
        engine = create_engine(f"sqlite:///{db_path}")
    else:
        engine = create_engine(connection_string)

    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        # Required tables
        required_tables = {
            "DocumentMatch_metrics_scores": [
                "model_name",
                "MeanDocumentMatch_score",
                "WeightedDocumentMatch_score",
            ],
            "lexical_metrics_scores": [
                "model_name",
                "f1_score",
                "rouge_1_score",
                "rouge_2_score",
                "rouge_l_score",
                "exact_match_score",
                "question_path",
            ],
            "semanticSimilarity_metrics_scores": [
                "model_name",
                "semanticSimilarity_score",
            ],
            "answerCorrect_metrics_scores": ["model_name", "answerCorrect_score"],
        }

        # Filter tables that exist **and** have data
        available_tables = {}
        for table, columns in required_tables.items():
            if table in existing_tables:
                count_result = session.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
                if count_result > 0:
                    available_tables[table] = columns

        # If no tables have data, return empty DataFrame
        if not available_tables:
            print("Warning: No tables contain data. Returning empty DataFrame.")
            return pd.DataFrame()

        # Build SELECT clause dynamically
        select_columns = []
        joins = []
        first_table = None
        table_aliases = {}

        for table, columns in available_tables.items():
            alias = table[:3]  # Short alias for readability
            table_aliases[table] = alias
            if first_table is None:
                first_table = table  # The base table
            else:
                # Use LEFT JOIN to keep all model results even if they don't exist in other tables
                joins.append(
                    f'LEFT JOIN "{table}" AS {alias} ON {table_aliases[first_table]}.model_name = {alias}.model_name'
                )

            # Use aliases in the SELECT clause
            for col in columns:
                select_columns.append(f'{alias}."{col}"')

        # Construct query dynamically
        query = text(
            f"""
        SELECT {", ".join(select_columns)}
        FROM "{first_table}" AS {table_aliases[first_table]}
        {" ".join(joins)}
        """
        )

        # Execute the query and fetch results
        result = session.execute(query)
        data = result.fetchall()

        # Convert the results to a pandas DataFrame
        df = pd.DataFrame(data, columns=result.keys())
        session.close()
        return df

    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return pd.DataFrame()
    finally:
        engine.dispose()


def delete_model_from_database(model_name: str, db_name: str = "benchmark.db", connection_string: str = None):
    """Delete all records for a specific model across all benchmark tables.

    Args:
        model_name: Name of the model to delete
        db_name: Database name if using SQLite
        connection_string: Optional connection string for external database
    """

    if connection_string is None:
        db_path = os.path.join(os.getcwd(), db_name)
        engine = create_engine(f"sqlite:///{db_path}")
    else:
        engine = create_engine(connection_string)

    tables = [
        LexicalMetricsScores.__tablename__,
        SemanticSimilarityScores.__tablename__,
        answerCorrectScores.__tablename__,
        DocumentMatchScores.__tablename__,
    ]

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Delete records from each table
        total_deleted = 0
        for table in tables:
            # Use text() for table names to handle special characters
            query = text(f'DELETE FROM "{table}" WHERE model_name = :model_name')
            result = session.execute(query, {"model_name": model_name})
            deleted_count = result.rowcount
            total_deleted += deleted_count
            print(f"Deleted {deleted_count} records from {table}")

        session.commit()
        print(f"Successfully deleted {total_deleted} total records for model: {model_name}")

    except Exception as e:
        session.rollback()
        print(f"Error deleting model data: {e}")
        raise
    finally:
        session.close()
        engine.dispose()
