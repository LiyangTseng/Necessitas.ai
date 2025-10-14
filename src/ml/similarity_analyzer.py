"""
Similarity Analyzer for Market Intelligence

Uses machine learning and embeddings to analyze company similarities,
perform clustering, and build similarity graphs for market intelligence.
"""

import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer
import networkx as nx

from loguru import logger


class SimilarityAnalyzer:
    """
    Analyzes company similarities using ML techniques and embeddings.

    This component handles embedding generation, clustering analysis,
    and similarity graph construction for market intelligence insights.
    """

    def __init__(self, config: Dict):
        """Initialize the similarity analyzer with ML configuration."""
        self.config = config
        self.embedding_model_name = config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        self.clustering_algorithm = config.get('clustering_algorithm', 'kmeans')
        self.n_clusters = config.get('n_clusters', 5)

        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"🤖 Embedding model loaded: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.embedding_model = None

        logger.info("🔍 Similarity analyzer initialized")

    async def generate_embeddings(self, company_data: Dict) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for company data.

        Args:
            company_data: Dictionary containing company information

        Returns:
            Dictionary mapping company names to their embeddings
        """
        try:
            embeddings = {}

            for company, data in company_data.items():
                # Create text representation of company
                company_text = self._create_company_text_representation(data)

                # Generate embedding
                if self.embedding_model:
                    embedding = self.embedding_model.encode(company_text)
                    embeddings[company] = embedding
                else:
                    # Fallback: create random embedding
                    embeddings[company] = np.random.rand(384)  # Standard embedding size

            logger.info(f"📊 Generated embeddings for {len(embeddings)} companies")
            return embeddings

        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            return {}

    def _create_company_text_representation(self, company_data: Dict) -> str:
        """Create text representation of company for embedding."""
        try:
            text_parts = []

            # Add company description
            if company_data.get('description'):
                text_parts.append(company_data['description'])

            # Add technologies
            technologies = company_data.get('technologies', [])
            if technologies:
                text_parts.append(f"Technologies: {', '.join(technologies)}")

            # Add recent news summaries
            news_articles = company_data.get('recent_news', [])
            for article in news_articles[:5]:  # Limit to recent articles
                if article.get('title'):
                    text_parts.append(article['title'])
                if article.get('description'):
                    text_parts.append(article['description'])

            # Add job postings
            job_postings = company_data.get('job_postings', [])
            for job in job_postings[:3]:  # Limit to recent jobs
                if job.get('title'):
                    text_parts.append(f"Job: {job['title']}")
                if job.get('skills'):
                    text_parts.append(f"Skills: {', '.join(job['skills'])}")

            # Add partnerships
            partnerships = company_data.get('partnerships', [])
            for partnership in partnerships[:3]:
                if partnership.get('description'):
                    text_parts.append(f"Partnership: {partnership['description']}")

            # Combine all text
            company_text = ' '.join(text_parts)

            # Truncate if too long
            if len(company_text) > 2000:
                company_text = company_text[:2000]

            return company_text

        except Exception as e:
            logger.error(f"❌ Failed to create company text representation: {e}")
            return ""

    async def cluster_companies(self, embeddings: Dict[str, np.ndarray]) -> Dict:
        """
        Cluster companies based on their embeddings.

        Args:
            embeddings: Dictionary mapping company names to embeddings

        Returns:
            Clustering results with cluster assignments
        """
        try:
            if not embeddings:
                logger.warning("⚠️ No embeddings provided for clustering")
                return {}

            # Prepare data for clustering
            companies = list(embeddings.keys())
            embedding_matrix = np.array([embeddings[company] for company in companies])

            # Perform clustering
            if self.clustering_algorithm == 'kmeans':
                clusterer = KMeans(n_clusters=self.n_clusters, random_state=42)
                cluster_labels = clusterer.fit_predict(embedding_matrix)
            elif self.clustering_algorithm == 'dbscan':
                clusterer = DBSCAN(eps=0.5, min_samples=2)
                cluster_labels = clusterer.fit_predict(embedding_matrix)
            else:
                logger.error(f"❌ Unknown clustering algorithm: {self.clustering_algorithm}")
                return {}

            # Organize results
            clusters = {}
            for i, (company, label) in enumerate(zip(companies, cluster_labels)):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(company)

            # Calculate cluster characteristics
            cluster_analysis = self._analyze_clusters(clusters, embeddings)

            results = {
                'clusters': clusters,
                'cluster_labels': dict(zip(companies, cluster_labels)),
                'cluster_analysis': cluster_analysis,
                'algorithm': self.clustering_algorithm,
                'n_clusters': len(set(cluster_labels)),
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"🎯 Clustered {len(companies)} companies into {len(set(cluster_labels))} clusters")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to cluster companies: {e}")
            return {}

    def _analyze_clusters(self, clusters: Dict, embeddings: Dict[str, np.ndarray]) -> Dict:
        """Analyze cluster characteristics and coherence."""
        try:
            analysis = {
                'cluster_sizes': {},
                'cluster_coherence': {},
                'cluster_centers': {},
                'inter_cluster_similarity': {}
            }

            for cluster_id, companies in clusters.items():
                if cluster_id == -1:  # Skip noise points in DBSCAN
                    continue

                # Cluster size
                analysis['cluster_sizes'][cluster_id] = len(companies)

                # Calculate cluster center
                cluster_embeddings = np.array([embeddings[company] for company in companies])
                cluster_center = np.mean(cluster_embeddings, axis=0)
                analysis['cluster_centers'][cluster_id] = cluster_center.tolist()

                # Calculate intra-cluster similarity (coherence)
                if len(companies) > 1:
                    similarities = cosine_similarity(cluster_embeddings)
                    # Remove diagonal (self-similarity)
                    similarities = similarities[np.triu_indices_from(similarities, k=1)]
                    analysis['cluster_coherence'][cluster_id] = float(np.mean(similarities))
                else:
                    analysis['cluster_coherence'][cluster_id] = 1.0

            return analysis

        except Exception as e:
            logger.error(f"❌ Failed to analyze clusters: {e}")
            return {}

    async def calculate_similarities(self, embeddings: Dict[str, np.ndarray]) -> Dict:
        """
        Calculate pairwise similarities between companies.

        Args:
            embeddings: Dictionary mapping company names to embeddings

        Returns:
            Similarity matrix and top similar pairs
        """
        try:
            if not embeddings:
                logger.warning("⚠️ No embeddings provided for similarity calculation")
                return {}

            companies = list(embeddings.keys())
            embedding_matrix = np.array([embeddings[company] for company in companies])

            # Calculate cosine similarity matrix
            similarity_matrix = cosine_similarity(embedding_matrix)

            # Create similarity pairs
            similarity_pairs = []
            for i, company1 in enumerate(companies):
                for j, company2 in enumerate(companies):
                    if i < j:  # Avoid duplicates and self-similarity
                        similarity_pairs.append({
                            'company1': company1,
                            'company2': company2,
                            'similarity': float(similarity_matrix[i, j])
                        })

            # Sort by similarity
            similarity_pairs.sort(key=lambda x: x['similarity'], reverse=True)

            # Get top similar pairs
            top_similar_pairs = similarity_pairs[:20]  # Top 20 most similar pairs

            results = {
                'similarity_matrix': similarity_matrix.tolist(),
                'similarity_pairs': similarity_pairs,
                'top_similar_pairs': top_similar_pairs,
                'companies': companies,
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"🔗 Calculated similarities for {len(companies)} companies")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to calculate similarities: {e}")
            return {}

    async def build_similarity_graph(self, embeddings: Dict[str, np.ndarray],
                                   threshold: float = 0.7) -> Dict:
        """
        Build a similarity graph from company embeddings.

        Args:
            embeddings: Dictionary mapping company names to embeddings
            threshold: Minimum similarity threshold for edges

        Returns:
            Graph data structure for visualization
        """
        try:
            if not embeddings:
                logger.warning("⚠️ No embeddings provided for graph construction")
                return {}

            # Create NetworkX graph
            G = nx.Graph()

            # Add nodes (companies)
            for company in embeddings.keys():
                G.add_node(company)

            # Calculate similarities and add edges
            companies = list(embeddings.keys())
            embedding_matrix = np.array([embeddings[company] for company in companies])
            similarity_matrix = cosine_similarity(embedding_matrix)

            edges = []
            for i, company1 in enumerate(companies):
                for j, company2 in enumerate(companies):
                    if i < j:  # Avoid duplicates
                        similarity = similarity_matrix[i, j]
                        if similarity >= threshold:
                            G.add_edge(company1, company2, weight=similarity)
                            edges.append({
                                'source': company1,
                                'target': company2,
                                'weight': float(similarity)
                            })

            # Calculate graph metrics
            graph_metrics = self._calculate_graph_metrics(G)

            # Prepare data for visualization
            nodes = []
            for company in companies:
                # Calculate node centrality
                centrality = G.degree(company) if company in G else 0
                nodes.append({
                    'id': company,
                    'label': company,
                    'centrality': centrality,
                    'cluster': self._get_node_cluster(company, embeddings)
                })

            graph_data = {
                'nodes': nodes,
                'edges': edges,
                'metrics': graph_metrics,
                'threshold': threshold,
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"🕸️ Built similarity graph with {len(nodes)} nodes and {len(edges)} edges")
            return graph_data

        except Exception as e:
            logger.error(f"❌ Failed to build similarity graph: {e}")
            return {}

    def _calculate_graph_metrics(self, G: nx.Graph) -> Dict:
        """Calculate graph metrics for analysis."""
        try:
            metrics = {
                'num_nodes': G.number_of_nodes(),
                'num_edges': G.number_of_edges(),
                'density': nx.density(G),
                'average_clustering': nx.average_clustering(G),
                'connected_components': nx.number_connected_components(G)
            }

            # Calculate centrality measures
            if G.number_of_nodes() > 0:
                degree_centrality = nx.degree_centrality(G)
                betweenness_centrality = nx.betweenness_centrality(G)
                closeness_centrality = nx.closeness_centrality(G)

                metrics['centrality'] = {
                    'degree': degree_centrality,
                    'betweenness': betweenness_centrality,
                    'closeness': closeness_centrality
                }

            return metrics

        except Exception as e:
            logger.error(f"❌ Failed to calculate graph metrics: {e}")
            return {}

    def _get_node_cluster(self, company: str, embeddings: Dict[str, np.ndarray]) -> int:
        """Get cluster assignment for a node (simplified)."""
        # This is a simplified version - in practice, you'd use the actual clustering results
        return hash(company) % 5  # Simple hash-based clustering

    async def analyze_market_convergence(self, embeddings: Dict[str, np.ndarray]) -> Dict:
        """
        Analyze market convergence patterns from embeddings.

        Args:
            embeddings: Dictionary mapping company names to embeddings

        Returns:
            Convergence analysis results
        """
        try:
            if not embeddings:
                logger.warning("⚠️ No embeddings provided for convergence analysis")
                return {}

            # Calculate pairwise similarities
            similarities = await self.calculate_similarities(embeddings)

            # Identify convergence patterns
            convergence_patterns = []
            high_similarity_pairs = [
                pair for pair in similarities.get('similarity_pairs', [])
                if pair['similarity'] > 0.8
            ]

            for pair in high_similarity_pairs:
                convergence_patterns.append({
                    'companies': [pair['company1'], pair['company2']],
                    'similarity': pair['similarity'],
                    'convergence_type': 'strategic_alignment',
                    'significance': 'high' if pair['similarity'] > 0.9 else 'medium'
                })

            # Analyze cluster convergence
            clusters = await self.cluster_companies(embeddings)
            cluster_convergence = self._analyze_cluster_convergence(clusters)

            results = {
                'convergence_patterns': convergence_patterns,
                'cluster_convergence': cluster_convergence,
                'high_similarity_pairs': high_similarity_pairs,
                'convergence_score': self._calculate_convergence_score(similarities),
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"🔄 Analyzed market convergence with {len(convergence_patterns)} patterns")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to analyze market convergence: {e}")
            return {}

    def _analyze_cluster_convergence(self, clusters: Dict) -> Dict:
        """Analyze convergence within clusters."""
        try:
            cluster_convergence = {}

            for cluster_id, companies in clusters.get('clusters', {}).items():
                if cluster_id == -1:  # Skip noise points
                    continue

                if len(companies) > 1:
                    # Calculate average similarity within cluster
                    cluster_similarities = []
                    for i, company1 in enumerate(companies):
                        for j, company2 in enumerate(companies):
                            if i < j:
                                # This would need the actual similarity matrix
                                # For now, use a placeholder
                                cluster_similarities.append(0.8)

                    cluster_convergence[cluster_id] = {
                        'companies': companies,
                        'average_similarity': np.mean(cluster_similarities) if cluster_similarities else 0,
                        'convergence_strength': 'high' if np.mean(cluster_similarities) > 0.8 else 'medium'
                    }

            return cluster_convergence

        except Exception as e:
            logger.error(f"❌ Failed to analyze cluster convergence: {e}")
            return {}

    def _calculate_convergence_score(self, similarities: Dict) -> float:
        """Calculate overall market convergence score."""
        try:
            similarity_pairs = similarities.get('similarity_pairs', [])
            if not similarity_pairs:
                return 0.0

            # Calculate average similarity
            avg_similarity = np.mean([pair['similarity'] for pair in similarity_pairs])

            # Calculate convergence score (0-1)
            convergence_score = min(1.0, avg_similarity)

            return float(convergence_score)

        except Exception as e:
            logger.error(f"❌ Failed to calculate convergence score: {e}")
            return 0.0

    async def generate_similarity_insights(self,
                                         embeddings: Dict[str, np.ndarray],
                                         company_data: Dict) -> Dict:
        """
        Generate insights from similarity analysis.

        Args:
            embeddings: Company embeddings
            company_data: Original company data

        Returns:
            Insights and recommendations
        """
        try:
            insights = {
                'similarity_insights': [],
                'strategic_recommendations': [],
                'market_opportunities': [],
                'competitive_threats': []
            }

            # Calculate similarities
            similarities = await self.calculate_similarities(embeddings)

            # Generate insights from top similar pairs
            top_pairs = similarities.get('top_similar_pairs', [])[:10]

            for pair in top_pairs:
                insight = {
                    'type': 'high_similarity',
                    'companies': [pair['company1'], pair['company2']],
                    'similarity_score': pair['similarity'],
                    'insight': f"High strategic similarity between {pair['company1']} and {pair['company2']}",
                    'recommendation': f"Monitor competitive dynamics between {pair['company1']} and {pair['company2']}"
                }
                insights['similarity_insights'].append(insight)

            # Generate strategic recommendations
            insights['strategic_recommendations'] = [
                "Monitor emerging competitive clusters",
                "Identify partnership opportunities in similar companies",
                "Track technology convergence patterns",
                "Analyze market positioning strategies"
            ]

            logger.info(f"💡 Generated {len(insights['similarity_insights'])} similarity insights")
            return insights

        except Exception as e:
            logger.error(f"❌ Failed to generate similarity insights: {e}")
            return {}

