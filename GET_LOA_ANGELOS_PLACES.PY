from main import ScouterPlaces
from config import CITY_DATA



scouter=ScouterPlaces()
scouter.main(CITY_DATA['LOS_ANGELOS']['ID'],"LOS_ANGELOS".lower(),CITY_DATA['LOS_ANGELOS']['COUNTRY'])