#!/usr/bin/env python3
"""
FLAC to Opus Album Converter
Scans music collection for albums containing FLAC files, allows selection, and converts to Opus format.
"""

import os
import subprocess
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

class FlacToOpusConverter:
    def __init__(self, music_root: str):
        self.music_root = Path(music_root)
        self.supported_formats = {'.flac'}
        self.opus_bitrate = '160k'
        
    def find_albums_with_flac(self) -> List[Dict[str, any]]:
        """Find all albums that contain FLAC files."""
        albums_with_flac = []
        
        print(f"Scanning for albums with FLAC files in {self.music_root}")
        
        for root, dirs, files in os.walk(self.music_root):
            # Skip the root directory itself
            if root == str(self.music_root):
                continue
                
            root_path = Path(root)
            flac_files = [f for f in files if f.lower().endswith('.flac')]
            
            if flac_files:
                # Calculate relative path from music root
                relative_path = root_path.relative_to(self.music_root)
                
                albums_with_flac.append({
                    'path': root_path,
                    'relative_path': str(relative_path),
                    'flac_count': len(flac_files),
                    'flac_files': flac_files,
                    'total_files': len(files)
                })
        
        return sorted(albums_with_flac, key=lambda x: x['relative_path'])
    
    def get_disk_space_info(self) -> Dict[str, str]:
        """Get disk space information for the music directory."""
        try:
            # Try using shutil.disk_usage first (more portable)
            total_bytes, used_bytes, free_bytes = shutil.disk_usage(str(self.music_root))
            
            # Convert to human readable format
            def format_bytes(bytes_value):
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if bytes_value < 1024.0:
                        return f"{bytes_value:.1f} {unit}"
                    bytes_value /= 1024.0
                return f"{bytes_value:.1f} PB"
            
            return {
                'total': format_bytes(total_bytes),
                'used': format_bytes(used_bytes),
                'free': format_bytes(free_bytes),
                'used_percent': f"{(used_bytes / total_bytes * 100):.1f}%"
            }
        except Exception:
            # Fallback to df command if shutil fails
            try:
                result = subprocess.run(['df', '-h', str(self.music_root)], 
                                      capture_output=True, text=True, check=True)
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 6:
                        return {
                            'total': parts[1],
                            'used': parts[2],
                            'free': parts[3],
                            'used_percent': parts[4]
                        }
            except Exception:
                pass
            
            return {
                'total': 'Unknown',
                'used': 'Unknown', 
                'free': 'Unknown',
                'used_percent': 'Unknown'
            }
    
    def display_disk_space(self) -> None:
        """Display current disk space information."""
        space_info = self.get_disk_space_info()
        print(f"\n📊 Disk Space Information:")
        print(f"   Total: {space_info['total']}")
        print(f"   Used:  {space_info['used']} ({space_info['used_percent']})")
        print(f"   Free:  {space_info['free']}")
    
    def display_albums(self, albums: List[Dict[str, any]]) -> None:
        """Display albums in a numbered list."""
        if not albums:
            print("No albums with FLAC files found!")
            return
            
        print(f"\nFound {len(albums)} albums with FLAC files:\n")
        print(f"{'#':<4} {'FLAC Files':<12} {'Album Path'}")
        print("-" * 80)
        
        for i, album in enumerate(albums, 1):
            print(f"{i:<4} {album['flac_count']:<12} {album['relative_path']}")
        
        # Display disk space information after the album list
        self.display_disk_space()
    
    def get_user_selection(self, albums: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Get user selection of albums to convert."""
        if not albums:
            return []
            
        self.display_albums(albums)
        
        while True:
            try:
                print(f"\nSelect albums to convert (1-{len(albums)}):")
                print("Examples: '1,3,5' or '1-5' or '1,3-7,10' or 'all'")
                selection = input("Selection: ").strip().lower()
                
                if selection == 'all':
                    return albums
                
                if not selection:
                    continue
                
                selected_indices = set()
                
                # Parse selection
                for part in selection.split(','):
                    part = part.strip()
                    if '-' in part:
                        # Range selection
                        start, end = map(int, part.split('-'))
                        selected_indices.update(range(start, end + 1))
                    else:
                        # Single selection
                        selected_indices.add(int(part))
                
                # Validate indices
                valid_indices = {i for i in selected_indices if 1 <= i <= len(albums)}
                if len(valid_indices) != len(selected_indices):
                    invalid = selected_indices - valid_indices
                    print(f"Invalid selections: {invalid}")
                    continue
                
                selected_albums = [albums[i-1] for i in sorted(valid_indices)]
                
                # Confirm selection
                print(f"\nSelected {len(selected_albums)} albums:")
                for album in selected_albums:
                    print(f"  - {album['relative_path']} ({album['flac_count']} FLAC files)")
                
                confirm = input("\nProceed with conversion? (Y/n): ").strip().lower()
                if confirm in ['n', 'no']:
                    print("Selection cancelled.")
                    continue
                else:
                    return selected_albums
                    
            except (ValueError, IndexError) as e:
                print(f"Invalid input: {e}")
                continue
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return []
    
    def check_opus_tools(self) -> bool:
        """Check if opus-tools (opusenc) is available."""
        try:
            result = subprocess.run(['opusenc', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"Found opus encoder: {result.stdout.strip().split()[0]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: opusenc not found. Please install opus-tools:")
            print("  macOS: brew install opus-tools")
            print("  Ubuntu/Debian: sudo apt install opus-tools")
            print("  Other: Check your package manager or download from opus-codec.org")
            return False
    
    def convert_flac_to_opus(self, flac_path: Path, opus_path: Path) -> bool:
        """Convert a single FLAC file to Opus format."""
        try:
            cmd = [
                'opusenc',
                '--bitrate', self.opus_bitrate,
                str(flac_path),
                str(opus_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error converting {flac_path.name}: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error converting {flac_path.name}: {e}")
            return False
    
    def handle_existing_opus_files(self, album: Dict[str, any]) -> List[Path]:
        """Handle FLAC files that already have corresponding Opus files."""
        album_path = album['path']
        flac_files = album['flac_files']
        
        # Find FLAC files that have corresponding Opus files
        flac_with_opus = []
        for flac_file in flac_files:
            flac_path = album_path / flac_file
            opus_file = flac_file.rsplit('.', 1)[0] + '.opus'
            opus_path = album_path / opus_file
            
            if opus_path.exists():
                flac_with_opus.append(flac_path)
        
        if flac_with_opus:
            print(f"  Found {len(flac_with_opus)} FLAC files with existing Opus versions")
            print(f"  Delete these FLAC files? (Y/n): ", end="")
            try:
                delete_choice = input().strip().lower()
                if delete_choice not in ['n', 'no']:
                    deleted_files = []
                    for flac_path in flac_with_opus:
                        try:
                            flac_path.unlink()
                            print(f"    Deleted: {flac_path.name}")
                            deleted_files.append(flac_path)
                        except Exception as e:
                            print(f"    Error deleting {flac_path.name}: {e}")
                    
                    # Clean up macOS metadata files for deleted FLAC files
                    if deleted_files:
                        print("    Cleaning up macOS metadata files...")
                        for flac_path in deleted_files:
                            metadata_file = album_path / f"._{flac_path.name}"
                            if metadata_file.exists():
                                try:
                                    metadata_file.unlink()
                                    print(f"      Deleted: {metadata_file.name}")
                                except Exception:
                                    pass
                    
                    return deleted_files
            except KeyboardInterrupt:
                print("\nSkipping deletion.")
        
        return []

    def convert_album(self, album: Dict[str, any]) -> bool:
        """Convert all FLAC files in an album to Opus format."""
        album_path = album['path']
        flac_files = album['flac_files']
        
        print(f"\nProcessing: {album['relative_path']}")
        
        # Handle existing Opus files first
        deleted_flac_files = self.handle_existing_opus_files(album)
        
        print(f"Converting {len(flac_files)} FLAC files to Opus...")
        
        successful_conversions = []
        failed_conversions = []
        
        # Convert files with thread pool for better performance
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {}
            
            for flac_file in flac_files:
                flac_path = album_path / flac_file
                opus_file = flac_file.rsplit('.', 1)[0] + '.opus'
                opus_path = album_path / opus_file
                
                # Skip if opus file already exists
                if opus_path.exists():
                    print(f"  Skipping {flac_file} (Opus version exists)")
                    continue
                
                future = executor.submit(self.convert_flac_to_opus, flac_path, opus_path)
                future_to_file[future] = (flac_file, flac_path, opus_path)
            
            # Process completed conversions
            for future in as_completed(future_to_file):
                flac_file, flac_path, opus_path = future_to_file[future]
                
                try:
                    success = future.result()
                    if success and opus_path.exists():
                        print(f"  ✓ Converted: {flac_file}")
                        successful_conversions.append(flac_path)
                    else:
                        print(f"  ✗ Failed: {flac_file}")
                        failed_conversions.append(flac_path)
                        
                except Exception as e:
                    print(f"  ✗ Error: {flac_file} - {e}")
                    failed_conversions.append(flac_path)
        
        # Report results
        total_files = len(flac_files)
        skipped = total_files - len(successful_conversions) - len(failed_conversions)
        
        print(f"  Results: {len(successful_conversions)} converted, {len(failed_conversions)} failed, {skipped} skipped")
        
        # Delete FLAC files if all conversions were successful
        if successful_conversions and not failed_conversions:
            print("  Deleting original FLAC files...")
            for flac_path in successful_conversions:
                try:
                    flac_path.unlink()
                    print(f"    Deleted: {flac_path.name}")
                except Exception as e:
                    print(f"    Error deleting {flac_path.name}: {e}")
            
            # Delete macOS metadata files (._* pattern)
            print("  Cleaning up macOS metadata files...")
            metadata_files = list(album_path.glob("._*"))
            for metadata_file in metadata_files:
                try:
                    metadata_file.unlink()
                    print(f"    Deleted: {metadata_file.name}")
                except Exception as e:
                    print(f"    Error deleting {metadata_file.name}: {e}")
            
            return True
        elif failed_conversions:
            print(f"  ⚠️  Keeping FLAC files due to {len(failed_conversions)} failed conversions")
            return False
        else:
            print("  No new conversions needed")
            return True
    
    def run(self) -> None:
        """Main execution flow."""
        print("FLAC to Opus Album Converter")
        print("=" * 40)
        
        # Check if opus tools are available
        if not self.check_opus_tools():
            sys.exit(1)
        
        # Find albums with FLAC files
        albums = self.find_albums_with_flac()
        
        if not albums:
            print("No albums with FLAC files found!")
            return
        
        # Get user selection
        selected_albums = self.get_user_selection(albums)
        
        if not selected_albums:
            print("No albums selected. Exiting.")
            return
        
        # Process selected albums
        print(f"\n{'='*60}")
        print("STARTING CONVERSION PROCESS")
        print(f"{'='*60}")
        
        successful_albums = 0
        
        for i, album in enumerate(selected_albums, 1):
            print(f"\n[{i}/{len(selected_albums)}]", end=" ")
            
            if self.convert_album(album):
                successful_albums += 1
        
        # Final summary
        print(f"\n{'='*60}")
        print("CONVERSION COMPLETE")
        print(f"{'='*60}")
        print(f"Successfully processed: {successful_albums}/{len(selected_albums)} albums")
        
        if successful_albums < len(selected_albums):
            print("Some albums had conversion errors. Check the output above for details.")
        
        # Display disk space after conversion
        self.display_disk_space()
        
        # Ask if user wants to continue with more conversions
        print(f"\nWould you like to convert more albums? (Y/n): ", end="")
        try:
            continue_choice = input().strip().lower()
            if continue_choice not in ['n', 'no']:
                print("\nRestarting conversion process...")
                self.run()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")


def main():
    """Entry point for the script."""
    parser = argparse.ArgumentParser(description='Convert FLAC files to Opus format')
    parser.add_argument('music_root', help='Root directory containing music albums')
    
    args = parser.parse_args()
    
    # Validate the provided path
    music_path = Path(args.music_root)
    if not music_path.exists():
        print(f"Error: Music directory '{args.music_root}' does not exist")
        sys.exit(1)
    
    if not music_path.is_dir():
        print(f"Error: '{args.music_root}' is not a directory")
        sys.exit(1)
    
    try:
        converter = FlacToOpusConverter(str(music_path.resolve()))
        converter.run()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()