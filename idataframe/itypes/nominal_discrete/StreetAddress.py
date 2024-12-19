import re
import pandas as pd

from idataframe.itypes.nominal_discrete.Text import Text
from idataframe.fields.StrField import StrField

__all__ = ['StreetAddressUS']

# list containing all street suffixes and abbreviations
SUFFIX_EN_LIST = [options_str.split(',') for options_str in re.sub(r"\s", '', """
alley,allee,ally,aly|anex,annex,annx,anx|arcade,arc|
avenue,av,aven,avenu,avn,avnue,ave|bayou,bayoo,byu|beach,bch|bend,bnd|
bluff,bluf,blf|bluffs,blfs|bottom,bot,bottm,btm|boulevard,boul,boulv,blvd|
branch,brnch,br|bridge,brdge,brg|brook,brk|brooks,brks|burg,bg|burgs,bgs|
bypass,bypa,bypas,byps,byp|camp,cmp,cp|canyon,canyn,cnyn,cyn|cape,cpe|
causeway,causwa,cswy|center,cen,cent,centr,centre,cnter,cntr,ctr|centers,ctrs|
circle,circ,circl,crcl,crcle,cir|circles,cirs|cliff,clf|cliffs,clfs|club,clb|
common,cmn|commons,cmns|corner,cor|corners,cors|course,crse|court,ct|cove,cv|
coves,cvs|creek,crk|crescent,crsent,crsnt,cres|crest,crst|crossing,crssng,xing|
crossroad,xrd|crossroads,xrds|curve,curv|dale,dl|dam,dm|divide,div,dvd,dv|
drive,driv,drv,dr|drives,drs|estate,est|estates,ests|
expressway,exp,expr,express,expw,expy|extension,extn,extnsn,ext|
extensions,exts|fall|falls,fls|ferry,frry,fry|field,fld|fiels,flds|flat,flt|
flats,flts|ford,frd|fords,frds|forest,forests,frst|forge,forg,frg|forges,frgs|
fork,frk|forks,frks|fort,frt,ft|freeway,freewy,frway,frwy,fwy|
garden,gardn,grden,grdn,gdn|gardens,gdns,gdns|gateway,gatewy,gatway,gtway,gtwy|
glen,gln|glens,glns|green,grn|greens,grns|grove,grov,grv|groves,grvs|
harbor,harb,harbr,hrbor,hbr|harbors,hbrs|haven,hvn|heights,ht,hts|
highway,highwy,hiway,hiwy,hway,hwy|hill,hl|hills,hls|
hollow,hllw,hollows,holws,holw|inlet,inlt|island,islnd,is|islands,islnds,iss|
isle,isles,isle|junction,jction,jctn,junctn,juncton,jct|junctions,jctns,jcts|
key,ky|keys,kys|knoll,knol,knl|knolls,knls|lake,lk|lakes,lks|land|light,lgt|
lights,lgts|loaf,lf|lock,lck|locks,lcks|lodge,ldge,lodg,ldg|loop,loops,loop|
mall|manor,mnr|manors,mnrs|meadow,mdw|meadows,medows,mdws|mews|mill,ml|
mills,mls|mission,missn,mssn,msn|motorway,mtwy|mount,mnt,mt|
mountain,mntain,mntn,mountin,mtin,mtn|mountains,mntns,mtns|neck,nck|
orchard,orchrd,orch|oval,ovl|overpass,opas|park,prk,parks,prks,park|
parkway,parkwy,pkway,pky,parkways,pkwys,pkwy|pass|passage,psge|path,paths,path|
pike,pikes,pike|pine,pne|pines,pnes|place,pl|plain,pln|plains,plns|
plaza,plza,plz|point,pt|points,pts|port,prt|ports,prts|prairie,prr,pr|
radial,rad,radiel,radl|ramp|ranch,ranches,rnchs,rnch|rapid,rpd|rapids,rpds|
rest,rst|ridge,rdge,rdg|ridges,rdgs|river,rvr,rivr,riv|road,rd|roads,rds|
route,rte|row|rue|run|shoal,shl|shoals,shls|shore,shoar,shr|shores,shoars,shrs|
skyway,skwy|spring,sprng,spng,spg|springs,spngs,sprngs,spgs|spur|spurs|
square,sqr,sqre,squ,sq|squares,sqrs,sqs|station,statn,stn,sta|
stravenue,strav,straven,stravn,strvn,strvnue,stra|stream,streme,strm|
street,strt,str,st|streets,sts|summit,sumitt,sumit,smt|terrace,terr,ter|
throughway,trwy|trace,traces,trce|track,tracks,trk,trks,trak|trafficway,trfy|
trail,trails,trls,trl|trailer,trlrs,trlr|tunnel,tunel,tunls,tunnels,tunnl,tunl|
turnpike,turnpk,trnpk,tpke|underpass,upas|union,un|unions,uns|
valley,vally,vlly,vly|vallyes,vlys|viaduct,vdct,viadct,via|view,vw|views,vws|
village,vill,villag,village,villg,villiage,vlg|villages,vlgs|ville,vl|
vista,vist,vst,vsta,vis|walk,walks,walk|wall|way,wy|ways,wys|well,wl|wells,wls
    """).split('|')]

# mapping dict to get full names
SUFFIX_EN_TO_FULL_DICT = { option : options[0] for options in SUFFIX_EN_LIST for option in options[1:] if len(options) > 1 }

# mapping dict to get abbreviations
SUFFIX_EN_TO_ABBR_DICT = { option : options[-1] for options in SUFFIX_EN_LIST for option in options[:-1] if len(options) > 1 }

# list containing all directions
DIRECTION_EN_DATA = [ el.split(',') for el in re.sub(r"\s", '', """
north|east|south|west|north,east|south,east|north,west|south,west
    """).split('|') ]

# regexp string to check all variants of directions
DIRECTION_EN_RE = '|'.join(
    ['[{}{}]\.?(?:\.)?(?:{}|{})?'.format(
        el[0][0].upper(), el[0][0].lower(),
        el[0][1:].upper(), el[0][1:].lower())
    for el in DIRECTION_EN_DATA if len(el) == 1]
    +
    ['[{}{}]\.?(?:{}|{})?[{}{}]\.?(?:{}|{})?'.format(
        el[0][0].upper(), el[0][0].lower(),
        el[0][1:].upper(), el[0][1:].lower(),
        el[1][0].upper(), el[1][0].lower(),
        el[1][1:].upper(), el[1][1:].lower())
    for el in DIRECTION_EN_DATA if len(el) == 2]
)

# mapping dict to get full names
DIRECTION_EN_TO_FULL_DICT = {
    **{ el[0] : el[0]
           for el in DIRECTION_EN_DATA if len(el) == 1 },
    **{ el[0][0] : el[0]
           for el in DIRECTION_EN_DATA if len(el) == 1 },
    **{ (el[0] + el[1]) : (el[0] + el[1])
           for el in DIRECTION_EN_DATA if len(el) == 2 },
    **{ (el[0][0] + el[1][0]) : (el[0] + el[1])
           for el in DIRECTION_EN_DATA if len(el) == 2 }
}

# mapping dict to get abbreviations
DIRECTION_EN_TO_ABBR_DICT = {
    **{ el[0] : el[0][0]
           for el in DIRECTION_EN_DATA if len(el) == 1 },
    **{ el[0][0] : el[0][0]
           for el in DIRECTION_EN_DATA if len(el) == 1 },
    **{ (el[0] + el[1]) : (el[0][0] + el[1][0])
           for el in DIRECTION_EN_DATA if len(el) == 2 },
    **{ (el[0][0] + el[1][0]) : (el[0][0] + el[1][0])
           for el in DIRECTION_EN_DATA if len(el) == 2 }
}

# -----------------------------------------------------------------------------

class StreetAddressUS(Text):
    """
    Post address US. Subclass of Text.
    https://zip.postcodebase.com/US_address_format
    https://pe.usps.com/text/pub28/28apc_002.htm
    """

    RE_PRIMARY_ADDRESS_NUMBER = r"[0-9\-/]+[a-zA-Z]?"
    RE_PRIMARY_ADDRESS_DIRECTION = DIRECTION_EN_RE
    RE_PRIMARY_ADDRESS_STREET = r"[a-zA-Z0-9.' ]+"
    RE_SECUNDARY_ADDRESS = r".*"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:   # StreetAddressUS type called directly
            Text.__init__(self, series, (
                ('address', StrField()),
                ('number', StrField()),
                ('direction', StrField(self.parse_direction)),
                ('street', StrField(self.parse_street)),
                ('secundary', StrField(self.parse_secundary)),
            ))
        else:   # subtype of StreetAddressUS called
            Text.__init__(self, series, fields)

        if fields is None:
            self.add_pre_parse_fn(self.pre_parse)

            self.add_match(name = 'number direction street, secundary',
                       regexp = r"^(?P<number>{})[ ]+(?P<direction>{})[ ]+(?P<street>{})[ ]*[,#][ ]*(?P<secundary>{})$".format(
                                self.RE_PRIMARY_ADDRESS_NUMBER,
                                self.RE_PRIMARY_ADDRESS_DIRECTION,
                                self.RE_PRIMARY_ADDRESS_STREET,
                                self.RE_SECUNDARY_ADDRESS),
                       str_format = '{number} {direction} {street}, {secundary}')

            self.add_match(name = 'number street direction, secundary',
                       regexp = r"^(?P<number>{})[ ]+(?P<street>{})[ ]+(?P<direction>{})[ ]*[,#][ ]*(?P<secundary>{})$".format(
                                self.RE_PRIMARY_ADDRESS_NUMBER,
                                self.RE_PRIMARY_ADDRESS_STREET,
                                self.RE_PRIMARY_ADDRESS_DIRECTION,
                                self.RE_SECUNDARY_ADDRESS),
                       str_format = '{number} {direction} {street}, {secundary}')

            self.add_match(name = 'number street, secundary',
                       regexp = r"^(?P<number>{})[ ]+(?P<street>{})[ ]*[,#][ ]*(?P<secundary>{})$".format(
                                self.RE_PRIMARY_ADDRESS_NUMBER,
                                self.RE_PRIMARY_ADDRESS_STREET,
                                self.RE_SECUNDARY_ADDRESS),
                       str_format = '{number} {street}, {secundary}')

            self.add_match(name = 'number direction street',
                       regexp = r"^(?P<number>{})[ ]+(?P<direction>{})[ ]+(?P<street>{})$".format(
                                self.RE_PRIMARY_ADDRESS_NUMBER,
                                self.RE_PRIMARY_ADDRESS_DIRECTION,
                                self.RE_PRIMARY_ADDRESS_STREET),
                       str_format = '{number} {direction} {street}')

            self.add_match(name = 'number street direction',
                       regexp = r"^(?P<number>{})[ ]+(?P<street>{})[ ]+(?P<direction>{})$".format(
                                self.RE_PRIMARY_ADDRESS_NUMBER,
                                self.RE_PRIMARY_ADDRESS_STREET,
                                self.RE_PRIMARY_ADDRESS_DIRECTION),
                       str_format = '{number} {direction} {street}')

            self.add_match(name = 'number street',
                       regexp = r"^(?P<number>{})[ ]+(?P<street>{})$".format(
                                self.RE_PRIMARY_ADDRESS_NUMBER,
                                self.RE_PRIMARY_ADDRESS_STREET),
                       str_format = '{number} {street}')

            self.add_match(name = 'direction street',
                       regexp = r"^(?P<direction>{})[ ]+(?P<street>{})$".format(
                                self.RE_PRIMARY_ADDRESS_DIRECTION,
                                self.RE_PRIMARY_ADDRESS_STREET),
                       str_format = '{direction} {street}')

            self.add_match(name = 'street direction',
                       regexp = r"^(?P<street>{})[ ]+(?P<direction>{})$".format(
                                self.RE_PRIMARY_ADDRESS_STREET,
                                self.RE_PRIMARY_ADDRESS_DIRECTION),
                       str_format = '{direction} {street}')

            self.add_match(name = 'street',
                       regexp = r"^(?P<street>{})$".format(
                               self.RE_PRIMARY_ADDRESS_STREET),
                       str_format = '{street}')

    def pre_parse(self, value:str) -> str:
        value = re.sub(r"\b[Nn]/?[Aa]\b", '', value)   # remove 'NA' parts inside string
        value = re.sub(r"\s{2,}", ' ', value.strip())  # convert multiple spaces to one space character
        return value

    def parse_direction(self, value:str) -> str:
        value = value.lower()
        for direction, new_direction in DIRECTION_EN_TO_ABBR_DICT.items():   # instead of ABBR, also FULL is possible
            value = re.sub(r"\b" + direction + r"\b", new_direction, value)
        value = value.upper()
        return value

    def parse_street(self, value:str) -> str:
        value = value.strip().lower()
        for suffix, new_suffix in SUFFIX_EN_TO_FULL_DICT.items():   # instead of FULL, also ABBR is possible
            value = re.sub(r"\b" + suffix + r"\b", new_suffix, value)
        value = value.title()
        value = re.sub(r"([1])St", '\g<1>st', value)
        value = re.sub(r"([2])Nd", '\g<1>nd', value)
        value = re.sub(r"([3])Rd", '\g<1>rd', value)
        value = re.sub(r"([04-9])Th", '\g<1>th', value)
        return value

    def parse_secundary(self, value:str) -> str:
        value = re.sub(r"\s{2,}", ' ', value.strip())
        value = value.upper()
        return value

    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([value.strip() for value in """
            280   WEST 3RD STREET
            422 WEST 20TH   STR
            421 MANHATTAN AVE
            DELANCEY STREET
            NAGLE AVENUE NORTHEAST
            250 WEST 27TH   STREET, 3B
            320 CENTRAL PARK WEST, 4a
            N BROADWAY
            7 GRACIE SQUARE    NORTH
        """.strip().split('\n')]), *args, **kwargs)
