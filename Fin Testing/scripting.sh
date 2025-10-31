# Runs many_sims.py with different fin shapes and wind speeds

source ./.venv/bin/activate

wind_speeds=(0 5 10 15 20)
fin_shapes=("Tapered Swept" "Swept" "Trapezoidal" "Elliptical")

for fin_shape in "${fin_shapes[@]}"; do
    for wind_speed in "${wind_speeds[@]}"; do
        python "./Fin Testing/many_sims.py" --fin_shape "$fin_shape" --wind_speed "$wind_speed"
    done
done