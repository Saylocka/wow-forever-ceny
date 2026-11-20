# wow-forever-ceny

Historie cen AH pro WoW Forever (EU, realm PvP Horde). GitHub Actions každou hodinu spustí
`collect.py`, který stáhne veřejná data TSM, ale jen když vyšel nový scan, a uloží je do
`data/RRRR/MM/DD/HHMM.csv.gz` (čas v UTC).

Lokálně si data stahuje `price_history.py` z projektu `wow` (web + addon ForeverCeny).

Pricing data from [TradeSkillMaster](https://tradeskillmaster.com).
