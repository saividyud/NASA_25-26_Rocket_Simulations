# Runs many_sims.py with different fin shapes and wind speeds

source ./.venv/bin/activate

wind_speeds=(0 5 9 10 13 15 20)

for wind_speed in "${wind_speeds[@]}"; do
    python "./Monte Carlo Sims FRR/many_sims.py" --wind_speed "$wind_speed"
done