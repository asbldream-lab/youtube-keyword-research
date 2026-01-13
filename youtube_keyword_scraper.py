#!/usr/bin/env python3
"""
YouTube Keyword Research Tool
Recherche des vidéos YouTube sur un sujet et extrait les commentaires les plus pertinents
pour faciliter l'analyse avec une IA.

Installation des dépendances:
pip install yt-dlp google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict
import argparse

try:
    from yt_dlp import YoutubeDL
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("❌ Dépendances manquantes. Veuillez installer avec:")
    print("pip install yt-dlp google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    exit(1)


class YouTubeKeywordResearcher:
    """Classe pour rechercher des vidéos YouTube et extraire les commentaires"""
    
    def __init__(self, max_videos: int = 10):
        """
        Initialise le chercheur
        
        Args:
            max_videos: Nombre maximum de vidéos à analyser
        """
        self.max_videos = max_videos
        self.youtube = None
        self.setup_youtube_api()
        
    def setup_youtube_api(self):
        """Configure l'API YouTube"""
        # Clé API YouTube (à remplacer par ta clé)
        # Obtiens ta clé: https://console.developers.google.com/
        API_KEY = os.getenv('YOUTUBE_API_KEY')
        
        if not API_KEY:
            print("⚠️  YOUTUBE_API_KEY non définie")
            print("Pour utiliser ce script, définis ta clé API YouTube:")
            print("export YOUTUBE_API_KEY='ta_clé_api'")
            print("\nSans clé API, le script sera limité.")
            return
            
        try:
            self.youtube = build('youtube', 'v3', developerKey=API_KEY)
        except Exception as e:
            print(f"❌ Erreur lors de la configuration de l'API: {e}")
    
    def search_videos(self, keyword: str) -> List[Dict]:
        """
        Recherche des vidéos YouTube sur un mot-clé
        
        Args:
            keyword: Le mot-clé de recherche
            
        Returns:
            Liste des IDs de vidéo trouvées
        """
        print(f"\n🔍 Recherche de vidéos pour: '{keyword}'")
        
        try:
            if not self.youtube:
                print("⚠️  API YouTube non configurée")
                return self._search_with_yt_dlp(keyword)
            
            request = self.youtube.search().list(
                q=keyword,
                part='snippet',
                type='video',
                maxResults=self.max_videos,
                order='relevance',
                relevanceLanguage='fr'
            )
            
            response = request.execute()
            videos = []
            
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                
                videos.append({
                    'id': video_id,
                    'title': title,
                    'channel': channel,
                    'url': f'https://www.youtube.com/watch?v={video_id}'
                })
                
                print(f"  ✓ Trouvé: {title[:60]}...")
            
            return videos
            
        except Exception as e:
            print(f"❌ Erreur de recherche: {e}")
            return []
    
    def _search_with_yt_dlp(self, keyword: str) -> List[Dict]:
        """Fallback: recherche avec yt-dlp si l'API n'est pas disponible"""
        print("  (Utilisation du mode yt-dlp)")
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{self.max_videos}:{keyword}"
                results = ydl.extract_info(search_query, download=False)
                
                videos = []
                for item in results.get('entries', []):
                    videos.append({
                        'id': item['id'],
                        'title': item['title'],
                        'channel': item.get('uploader', 'Inconnu'),
                        'url': f"https://www.youtube.com/watch?v={item['id']}"
                    })
                    print(f"  ✓ Trouvé: {item['title'][:60]}...")
                
                return videos
        except Exception as e:
            print(f"❌ Erreur yt-dlp: {e}")
            return []
    
    def get_video_comments(self, video_id: str, max_comments: int = 20) -> List[str]:
        """
        Récupère les meilleurs commentaires d'une vidéo
        
        Args:
            video_id: L'ID de la vidéo YouTube
            max_comments: Nombre maximum de commentaires à récupérer
            
        Returns:
            Liste des commentaires
        """
        try:
            if not self.youtube:
                print(f"    ⚠️  Impossible d'accéder aux commentaires (pas d'API)")
                return []
            
            comments = []
            request = self.youtube.commentThreads().list(
                videoId=video_id,
                part='snippet',
                textFormat='plainText',
                maxResults=min(100, max_comments),
                order='relevance'
            )
            
            while request and len(comments) < max_comments:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    # Nettoie le commentaire
                    comment = re.sub(r'http\S+|www\S+', '', comment)  # Enlève les URLs
                    comment = comment.strip()
                    
                    if len(comment) > 10:  # Filtre les commentaires trop courts
                        comments.append(comment)
                
                # Pagination
                if 'nextPageToken' in response and len(comments) < max_comments:
                    request = self.youtube.commentThreads().list(
                        videoId=video_id,
                        part='snippet',
                        textFormat='plainText',
                        pageToken=response['nextPageToken'],
                        maxResults=min(100, max_comments - len(comments)),
                        order='relevance'
                    )
                else:
                    request = None
            
            return comments[:max_comments]
            
        except Exception as e:
            print(f"    ⚠️  Erreur lors de la récupération des commentaires: {str(e)[:50]}")
            return []
    
    def generate_report(self, keyword: str, videos: List[Dict], all_comments: Dict) -> str:
        """
        Génère un rapport formaté avec les commentaires
        
        Args:
            keyword: Le mot-clé recherché
            videos: Liste des vidéos trouvées
            all_comments: Dictionnaire des commentaires par vidéo
            
        Returns:
            Rapport formaté en texte
        """
        report = []
        report.append("=" * 80)
        report.append(f"📊 RAPPORT DE RECHERCHE YOUTUBE - {keyword.upper()}")
        report.append("=" * 80)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Nombre de vidéos analysées: {len(videos)}\n")
        
        for idx, video in enumerate(videos, 1):
            report.append("-" * 80)
            report.append(f"VIDÉO {idx}: {video['title']}")
            report.append(f"Canal: {video['channel']}")
            report.append(f"URL: {video['url']}")
            report.append("")
            
            comments = all_comments.get(video['id'], [])
            if comments:
                report.append(f"📝 TOP {len(comments)} COMMENTAIRES:")
                report.append("")
                for i, comment in enumerate(comments, 1):
                    report.append(f"{i}. {comment}")
                    report.append("")
            else:
                report.append("❌ Aucun commentaire disponible pour cette vidéo")
                report.append("")
        
        report.append("=" * 80)
        report.append("✅ FIN DU RAPPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def run(self, keyword: str) -> str:
        """
        Lance la recherche complète
        
        Args:
            keyword: Le mot-clé à rechercher
            
        Returns:
            Le rapport généré
        """
        print(f"\n🚀 Démarrage de la recherche pour: '{keyword}'")
        print(f"📍 Nombre maximum de vidéos: {self.max_videos}")
        
        # Recherche les vidéos
        videos = self.search_videos(keyword)
        
        if not videos:
            print("❌ Aucune vidéo trouvée")
            return "Aucune vidéo trouvée pour cette recherche."
        
        print(f"\n✅ {len(videos)} vidéo(s) trouvée(s)")
        
        # Extrait les commentaires
        all_comments = {}
        print("\n💬 Récupération des commentaires...")
        
        for video in videos:
            print(f"  Traitement: {video['title'][:50]}...")
            comments = self.get_video_comments(video['id'], max_comments=20)
            all_comments[video['id']] = comments
            print(f"    → {len(comments)} commentaires récupérés")
        
        # Génère le rapport
        report = self.generate_report(keyword, videos, all_comments)
        
        return report


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Recherche YouTube - Extrait commentaires pour analyse IA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python youtube_keyword_scraper.py "guerre en Irak"
  python youtube_keyword_scraper.py "IA et avenir" --max-videos 15
  python youtube_keyword_scraper.py "changement climatique" > rapport.txt
        """
    )
    
    parser.add_argument(
        'keyword',
        help='Mot-clé ou sujet à rechercher'
    )
    parser.add_argument(
        '--max-videos',
        type=int,
        default=10,
        help='Nombre maximum de vidéos à analyser (défaut: 10)'
    )
    parser.add_argument(
        '--output',
        help='Fichier de sortie (défaut: affichage en console)'
    )
    
    args = parser.parse_args()
    
    # Lance la recherche
    researcher = YouTubeKeywordResearcher(max_videos=args.max_videos)
    report = researcher.run(args.keyword)
    
    # Sauvegarde ou affiche le résultat
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ Rapport sauvegardé dans: {args.output}")
    else:
        print("\n" + report)
    
    return report


if __name__ == '__main__':
    main()
