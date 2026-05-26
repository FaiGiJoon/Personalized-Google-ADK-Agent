import unittest
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from skills.security.security_skills import validate_snort_rule, validate_yara_rule
from skills.gaming.gaming_skills import optimize_pbr_team
from skills.models import SnortRuleSchema, PBRTeamSchema, YaraRuleSchema

class TestSkills(unittest.TestCase):

    def test_validate_snort_rule_valid(self):
        rule = 'alert tcp 1.2.3.4 any -> 5.6.7.8 80 (msg:"Test Rule"; sid:1000001;)'
        result = validate_snort_rule(SnortRuleSchema(rule=rule))
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["issues"]), 0)

    def test_validate_snort_rule_invalid_action(self):
        rule = 'invalid tcp any any -> any any (msg:"Test Rule"; sid:1000001;)'
        result = validate_snort_rule(SnortRuleSchema(rule=rule))
        self.assertFalse(result["valid"])
        self.assertIn("Rule must start with a valid action", result["issues"][0])

    def test_validate_snort_rule_missing_msg(self):
        rule = 'alert tcp any any -> any any (sid:1000001;)'
        result = validate_snort_rule(SnortRuleSchema(rule=rule))
        self.assertFalse(result["valid"])
        self.assertTrue(any("missing a 'msg'" in issue for issue in result["issues"]))

    def test_validate_snort_rule_invalid_protocol(self):
        rule = 'alert invalid_proto any any -> any any (msg:"Test"; sid:1000001;)'
        result = validate_snort_rule(SnortRuleSchema(rule=rule))
        self.assertFalse(result["valid"])
        self.assertTrue(any("Invalid or unsupported protocol" in issue for issue in result["issues"]))

    def test_validate_yara_rule_valid(self):
        rule = 'rule TestRule { condition: true }'
        result = validate_yara_rule(YaraRuleSchema(rule=rule))
        self.assertTrue(result["valid"])

    def test_validate_yara_rule_missing_keyword(self):
        rule = 'TestRule { condition: true }'
        result = validate_yara_rule(YaraRuleSchema(rule=rule))
        self.assertFalse(result["valid"])
        self.assertIn("Rule must start with the 'rule' keyword", result["issues"][0])

    def test_validate_yara_rule_missing_condition(self):
        rule = 'rule TestRule { strings: $a = "test" }'
        result = validate_yara_rule(YaraRuleSchema(rule=rule))
        self.assertFalse(result["valid"])
        self.assertIn("missing the mandatory 'condition:' section", result["issues"][0])

    def test_validate_yara_rule_missing_strings_section(self):
        rule = 'rule TestRule { condition: $a }'
        result = validate_yara_rule(YaraRuleSchema(rule=rule))
        self.assertFalse(result["valid"])
        self.assertTrue(any("references strings (via '$'), but the 'strings:' section is missing" in issue for issue in result["issues"]))

    def test_optimize_pbr_team_missing_item(self):
        team_data = {
            "pokemon": [
                {
                    "name": "Pikachu",
                    "moves": ["Thunderbolt", "Iron Tail", "Quick Attack", "Volt Tackle"],
                    "item": None
                }
            ]
        }
        result = optimize_pbr_team(PBRTeamSchema(team_data=team_data))
        self.assertTrue(any("missing a held item" in opt for opt in result["optimizations"]))
        self.assertTrue(any("'Life Orb'" in opt for opt in result["optimizations"]))

    def test_optimize_pbr_team_evasion(self):
        team_data = {
            "pokemon": [
                {
                    "name": "Blissey",
                    "moves": ["Soft-Boiled", "Toxic", "Seismic Toss", "Double Team"],
                    "item": "Leftovers"
                }
            ]
        }
        result = optimize_pbr_team(PBRTeamSchema(team_data=team_data))
        self.assertTrue(any("Evasion moves" in opt for opt in result["optimizations"]))

if __name__ == "__main__":
    unittest.main()
