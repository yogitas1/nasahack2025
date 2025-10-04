#!/usr/bin/env python3
"""
PDF Knowledge Extraction Script

This script processes PDF files to extract structured knowledge using OpenAI API
and generates embeddings for the extracted content.
"""

import os
import json
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

import PyPDF2
import openai
from openai import OpenAI
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class KeyRecommendation:
    infrastructure_type: str
    target_setting: str
    expected_impact: str
    implementation_steps: List[str]

@dataclass
class CaseStudy:
    country: str
    project: str
    outcome: str
    lessons: str

@dataclass
class ExtractedKnowledge:
    filename: str
    key_recommendations: List[KeyRecommendation]
    case_studies: List[CaseStudy]
    best_practices: List[str]
    challenges: List[str]

class PDFKnowledgeExtractor:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.knowledge_base: List[ExtractedKnowledge] = []
        self.embeddings_data: List[Dict[str, Any]] = []

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def extract_structured_knowledge(self, text: str, filename: str) -> ExtractedKnowledge:
        """Use OpenAI API to extract structured knowledge from text."""
        prompt = f"""
        Analyze the following research text and extract structured knowledge in JSON format.
        Focus on infrastructure development, policy recommendations, case studies, and implementation guidance.

        Return a JSON object with these exact fields:
        {{
            "key_recommendations": [
                {{
                    "infrastructure_type": "string - type of infrastructure (e.g., healthcare, transportation, digital)",
                    "target_setting": "string - target population or setting (e.g., rural areas, urban slums, developing countries)",
                    "expected_impact": "string - expected outcomes or benefits",
                    "implementation_steps": ["list of specific steps or actions needed"]
                }}
            ],
            "case_studies": [
                {{
                    "country": "string - country or region",
                    "project": "string - project name or description",
                    "outcome": "string - results achieved",
                    "lessons": "string - key lessons learned"
                }}
            ],
            "best_practices": ["list of best practice recommendations"],
            "challenges": ["list of key challenges or barriers identified"]
        }}

        Text to analyze:
        {text[:8000]}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured knowledge from research documents. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code block if present
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    content = content[start:end].strip()
                    data = json.loads(content)
                else:
                    raise

            # Convert to structured objects
            key_recommendations = [
                KeyRecommendation(**rec) for rec in data.get("key_recommendations", [])
            ]
            case_studies = [
                CaseStudy(**case) for case in data.get("case_studies", [])
            ]

            return ExtractedKnowledge(
                filename=filename,
                key_recommendations=key_recommendations,
                case_studies=case_studies,
                best_practices=data.get("best_practices", []),
                challenges=data.get("challenges", [])
            )

        except Exception as e:
            logger.error(f"Error extracting knowledge from {filename}: {e}")
            return ExtractedKnowledge(
                filename=filename,
                key_recommendations=[],
                case_studies=[],
                best_practices=[],
                challenges=[]
            )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using OpenAI embeddings API."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []

    def prepare_embedding_texts(self, knowledge: ExtractedKnowledge) -> List[Dict[str, Any]]:
        """Prepare texts and metadata for embedding generation."""
        embedding_items = []

        # Add recommendations
        for i, rec in enumerate(knowledge.key_recommendations):
            text = f"Infrastructure Type: {rec.infrastructure_type}. Target Setting: {rec.target_setting}. Expected Impact: {rec.expected_impact}. Implementation: {' '.join(rec.implementation_steps)}"
            embedding_items.append({
                "text": text,
                "type": "recommendation",
                "filename": knowledge.filename,
                "index": i,
                "metadata": asdict(rec)
            })

        # Add case studies
        for i, case in enumerate(knowledge.case_studies):
            text = f"Country: {case.country}. Project: {case.project}. Outcome: {case.outcome}. Lessons: {case.lessons}"
            embedding_items.append({
                "text": text,
                "type": "case_study",
                "filename": knowledge.filename,
                "index": i,
                "metadata": asdict(case)
            })

        return embedding_items

    def process_pdf_files(self, articles_dir: str = "articles") -> None:
        """Process all PDF files in the articles directory."""
        pdf_files = list(Path(articles_dir).glob("*.pdf"))[:10]  # Limit to 10 files

        logger.info(f"Processing {len(pdf_files)} PDF files...")

        all_embedding_items = []

        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}...")

            # Extract text
            text = self.extract_text_from_pdf(str(pdf_file))
            if not text.strip():
                logger.warning(f"No text extracted from {pdf_file.name}")
                continue

            # Extract structured knowledge
            knowledge = self.extract_structured_knowledge(text, pdf_file.name)
            self.knowledge_base.append(knowledge)

            # Prepare embedding texts
            embedding_items = self.prepare_embedding_texts(knowledge)
            all_embedding_items.extend(embedding_items)

        # Generate embeddings for all items
        if all_embedding_items:
            logger.info("Generating embeddings...")
            texts = [item["text"] for item in all_embedding_items]
            embeddings = self.generate_embeddings(texts)

            # Combine embeddings with metadata
            for item, embedding in zip(all_embedding_items, embeddings):
                item["embedding"] = embedding

            self.embeddings_data = all_embedding_items

    def save_knowledge_base(self, output_file: str = "knowledge_base.json") -> None:
        """Save the extracted knowledge base to a JSON file."""
        try:
            # Convert dataclasses to dictionaries for JSON serialization
            serializable_data = []
            for knowledge in self.knowledge_base:
                data = {
                    "filename": knowledge.filename,
                    "key_recommendations": [asdict(rec) for rec in knowledge.key_recommendations],
                    "case_studies": [asdict(case) for case in knowledge.case_studies],
                    "best_practices": knowledge.best_practices,
                    "challenges": knowledge.challenges
                }
                serializable_data.append(data)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Knowledge base saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")

    def save_embeddings(self, output_file: str = "embeddings.pkl") -> None:
        """Save the embeddings data to a pickle file."""
        try:
            with open(output_file, 'wb') as f:
                pickle.dump(self.embeddings_data, f)

            logger.info(f"Embeddings saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")

def main():
    """Main function to run the knowledge extraction process."""
    # Load environment variables from .env file
    load_dotenv()

    # Get OpenAI API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return

    # Initialize extractor
    extractor = PDFKnowledgeExtractor(api_key)

    # Process PDF files
    extractor.process_pdf_files()

    # Save results
    extractor.save_knowledge_base()
    extractor.save_embeddings()

    logger.info("Knowledge extraction completed successfully!")
    logger.info(f"Processed {len(extractor.knowledge_base)} documents")
    logger.info(f"Generated {len(extractor.embeddings_data)} embeddings")

if __name__ == "__main__":
    main()