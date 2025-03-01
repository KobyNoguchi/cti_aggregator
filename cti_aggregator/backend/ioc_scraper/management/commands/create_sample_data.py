from django.core.management.base import BaseCommand
from ioc_scraper.models import CrowdStrikeMalware
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Creates sample CrowdStrike malware family data for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to create sample CrowdStrike malware family data...'))
        
        # Sample malware families data
        malware_families = [
            {
                "malware_id": "mal1001",
                "name": "BlackCat Ransomware",
                "description": "BlackCat (also known as ALPHV) is a sophisticated ransomware-as-a-service (RaaS) operation that emerged in late 2021. It's notable for being written in Rust, which is unusual for ransomware and provides cross-platform capabilities.",
                "ttps": ["T1486: Data Encrypted for Impact", "T1490: Inhibit System Recovery", "T1082: System Information Discovery", "T1562.001: Disable or Modify Tools"],
                "targeted_industries": ["Healthcare", "Financial Services", "Manufacturing", "Critical Infrastructure"],
                "threat_groups": ["ALPHV", "BlackCat Affiliates"],
                "publish_date": datetime.now() - timedelta(days=180),
                "activity_start_date": datetime.now() - timedelta(days=500),
                "activity_end_date": None,
                "last_update_date": datetime.now() - timedelta(days=15)
            },
            {
                "malware_id": "mal1002",
                "name": "Conti Ransomware",
                "description": "Conti is a sophisticated ransomware variant that was first observed in 2020. It operates as a Ransomware-as-a-Service (RaaS) model and is known for its speed of encryption and its ability to target network resources.",
                "ttps": ["T1486: Data Encrypted for Impact", "T1489: Service Stop", "T1490: Inhibit System Recovery", "T1566: Phishing"],
                "targeted_industries": ["Healthcare", "Government", "Emergency Services", "Education"],
                "threat_groups": ["Wizard Spider", "Conti Group"],
                "publish_date": datetime.now() - timedelta(days=700),
                "activity_start_date": datetime.now() - timedelta(days=1000),
                "activity_end_date": datetime.now() - timedelta(days=100),
                "last_update_date": datetime.now() - timedelta(days=90)
            },
            {
                "malware_id": "mal1003",
                "name": "LockBit Ransomware",
                "description": "LockBit is a ransomware that operates as a Ransomware-as-a-Service (RaaS). It first appeared in September 2019 and has since evolved through multiple versions. LockBit is known for its self-spreading capabilities and efficient encryption.",
                "ttps": ["T1486: Data Encrypted for Impact", "T1490: Inhibit System Recovery", "T1566: Phishing", "T1190: Exploit Public-Facing Application"],
                "targeted_industries": ["Manufacturing", "Financial Services", "Legal Services", "Retail"],
                "threat_groups": ["LockBit Gang"],
                "publish_date": datetime.now() - timedelta(days=400),
                "activity_start_date": datetime.now() - timedelta(days=1200),
                "activity_end_date": None,
                "last_update_date": datetime.now() - timedelta(days=5)
            },
            {
                "malware_id": "mal1004",
                "name": "Emotet",
                "description": "Emotet is a sophisticated and modular banking Trojan that primarily functions as a downloader or dropper of other banking Trojans. It has evolved to become a distribution platform for other malware.",
                "ttps": ["T1566: Phishing", "T1204: User Execution", "T1027: Obfuscated Files or Information", "T1055: Process Injection"],
                "targeted_industries": ["Banking", "Finance", "Government", "Healthcare"],
                "threat_groups": ["TA542", "Mummy Spider"],
                "publish_date": datetime.now() - timedelta(days=1500),
                "activity_start_date": datetime.now() - timedelta(days=2000),
                "activity_end_date": None,
                "last_update_date": datetime.now() - timedelta(days=30)
            },
            {
                "malware_id": "mal1005",
                "name": "Trickbot",
                "description": "Trickbot is a sophisticated banking Trojan that has evolved into a modular malware platform. It is capable of stealing banking credentials, cryptocurrency wallets, and providing remote access to infected systems.",
                "ttps": ["T1566: Phishing", "T1204: User Execution", "T1059: Command and Scripting Interpreter", "T1543: Create or Modify System Process"],
                "targeted_industries": ["Banking", "Finance", "Healthcare", "Telecommunications"],
                "threat_groups": ["Wizard Spider"],
                "publish_date": datetime.now() - timedelta(days=1200),
                "activity_start_date": datetime.now() - timedelta(days=1800),
                "activity_end_date": None,
                "last_update_date": datetime.now() - timedelta(days=45)
            },
            {
                "malware_id": "mal1006",
                "name": "Ryuk Ransomware",
                "description": "Ryuk is a sophisticated ransomware that targets large organizations for high-value ransom payments. It is known for its targeted approach and manual deployment after initial compromise.",
                "ttps": ["T1486: Data Encrypted for Impact", "T1489: Service Stop", "T1490: Inhibit System Recovery", "T1083: File and Directory Discovery"],
                "targeted_industries": ["Healthcare", "Government", "Financial Services", "Education"],
                "threat_groups": ["Wizard Spider", "GRIM SPIDER"],
                "publish_date": datetime.now() - timedelta(days=900),
                "activity_start_date": datetime.now() - timedelta(days=1300),
                "activity_end_date": datetime.now() - timedelta(days=200),
                "last_update_date": datetime.now() - timedelta(days=180)
            },
            {
                "malware_id": "mal1007",
                "name": "Qakbot",
                "description": "Qakbot (also known as QBot, QuackBot, and Pinkslipbot) is a banking Trojan that has been active since 2008. It has evolved to include features for stealing banking credentials, deploying ransomware, and establishing persistence.",
                "ttps": ["T1566: Phishing", "T1204: User Execution", "T1055: Process Injection", "T1027: Obfuscated Files or Information"],
                "targeted_industries": ["Banking", "Finance", "Manufacturing", "Professional Services"],
                "threat_groups": ["TA570"],
                "publish_date": datetime.now() - timedelta(days=1100),
                "activity_start_date": datetime.now() - timedelta(days=5000),
                "activity_end_date": None,
                "last_update_date": datetime.now() - timedelta(days=20)
            },
            {
                "malware_id": "mal1008",
                "name": "Cobalt Strike",
                "description": "Cobalt Strike is a commercial penetration testing tool that is widely misused by threat actors. It provides a post-exploitation framework that can be used for lateral movement, command and control, and data exfiltration.",
                "ttps": ["T1059: Command and Scripting Interpreter", "T1055: Process Injection", "T1105: Ingress Tool Transfer", "T1572: Protocol Tunneling"],
                "targeted_industries": ["Government", "Defense", "Critical Infrastructure", "Technology"],
                "threat_groups": ["APT29", "APT41", "FIN7", "Various Threat Actors"],
                "publish_date": datetime.now() - timedelta(days=800),
                "activity_start_date": datetime.now() - timedelta(days=3000),
                "activity_end_date": None,
                "last_update_date": datetime.now() - timedelta(days=10)
            },
            {
                "malware_id": "mal1009",
                "name": "DarkSide Ransomware",
                "description": "DarkSide is a ransomware-as-a-service (RaaS) operation that gained notoriety after the Colonial Pipeline attack in May 2021. It employs a double extortion model, encrypting data and threatening to leak it if the ransom is not paid.",
                "ttps": ["T1486: Data Encrypted for Impact", "T1489: Service Stop", "T1490: Inhibit System Recovery", "T1082: System Information Discovery"],
                "targeted_industries": ["Energy", "Manufacturing", "Financial Services", "Transportation"],
                "threat_groups": ["DarkSide Group", "Carbon Spider"],
                "publish_date": datetime.now() - timedelta(days=600),
                "activity_start_date": datetime.now() - timedelta(days=800),
                "activity_end_date": datetime.now() - timedelta(days=300),
                "last_update_date": datetime.now() - timedelta(days=290)
            },
            {
                "malware_id": "mal1010",
                "name": "Maze Ransomware",
                "description": "Maze (also known as ChaCha) is a ransomware that pioneered the double extortion model, where data is exfiltrated before encryption and used as additional leverage for ransom payment.",
                "ttps": ["T1486: Data Encrypted for Impact", "T1489: Service Stop", "T1490: Inhibit System Recovery", "T1005: Data from Local System"],
                "targeted_industries": ["Healthcare", "Government", "Legal Services", "Manufacturing"],
                "threat_groups": ["Maze Team", "TA2101"],
                "publish_date": datetime.now() - timedelta(days=1000),
                "activity_start_date": datetime.now() - timedelta(days=1200),
                "activity_end_date": datetime.now() - timedelta(days=400),
                "last_update_date": datetime.now() - timedelta(days=390)
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for malware_data in malware_families:
            try:
                malware, created = CrowdStrikeMalware.objects.update_or_create(
                    malware_id=malware_data['malware_id'],
                    defaults=malware_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created malware family: {malware_data['name']}"))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"Updated malware family: {malware_data['name']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating/updating malware family {malware_data.get('name', 'unknown')}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Sample data creation complete. Created: {created_count}, Updated: {updated_count}")) 