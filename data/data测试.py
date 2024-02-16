from data_seele import seele
from data_klutz import klutz

seele.battle_star()
for attr_name, attr_value in vars(seele).items():
    print(f"{attr_name}: {attr_value}")
