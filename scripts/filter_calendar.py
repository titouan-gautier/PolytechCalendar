import requests
from icalendar import Calendar
import re
import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'groups.yml'
    with open(config_path) as f:
        return yaml.safe_load(f)

def filter_calendar():
    config = load_config()
    
    # Télécharger le calendrier
    response = requests.get(config['ical_url'])
    original_cal = Calendar.from_ical(response.text)
    
    # Créer nouveau calendrier
    filtered_cal = Calendar()
    filtered_cal.add('prodid', '-//Mon Calendrier Filtre//')
    filtered_cal.add('version', '2.0')
    
    # Filtrage
    for event in original_cal.walk('VEVENT'):
        desc = event.get('DESCRIPTION', '')
        
        matiere_match = re.search(r"Matière : (.+)", desc)
        remarque_match = re.search(r"Remarques : (.+)", desc)
        
        keep = True
        
        if matiere_match and remarque_match:
            matiere = matiere_match.group(1).lower()
            groupe = remarque_match.group(1).strip().lower()
            
            if matiere in config['filters']:
                has_group_info = any(group_letter.lower() in groupe for group_letter in ['A', 'B'])
                
                # Si les remarques contiennent des infos de groupe mais pas le bon groupe, filtrer
                if has_group_info and str(config['filters'][matiere]).lower() not in groupe:
                    keep = False
        
        if keep:
            filtered_cal.add_component(event)
    
    # Sauvegarder
    output_path = Path(__file__).parent.parent / 'docs' / 'filtered_calendar.ics'
    with open(output_path, 'wb') as f:
        f.write(filtered_cal.to_ical())

if __name__ == '__main__':
    filter_calendar()