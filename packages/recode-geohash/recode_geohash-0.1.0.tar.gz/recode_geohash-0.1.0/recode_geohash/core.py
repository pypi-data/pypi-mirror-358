BASE32_GEOHASH = "0123456789bcdefghjkmnpqrstuvwxyz"
BASE32_MAP = {c: i for i, c in enumerate(BASE32_GEOHASH)}

def geohash_para_bits(geohash):
    bits = []
    for c in geohash:
        valor = BASE32_MAP[c]
        for i in range(4, -1, -1):
            bits.append((valor >> i) & 1)
    return bits

def separar_bits(bits):
    lon_bits = bits[::2]
    lat_bits = bits[1::2]
    return lat_bits, lon_bits

def bits_para_num(bits, intervalo):
    min_val, max_val = intervalo
    for bit in bits:
        meio = (min_val + max_val) / 2
        if bit == 1:
            min_val = meio
        else:
            max_val = meio
    return (min_val + max_val) / 2

def coordenadas_do_geohash(geohash):
    bits = geohash_para_bits(geohash)
    lat_bits, lon_bits = separar_bits(bits)
    lat = bits_para_num(lat_bits, [-90.0, 90.0])
    lon = bits_para_num(lon_bits, [-180.0, 180.0])
    return lat, lon

def dividir_intervalo(valor, intervalo, bits):
    resultado = []
    min_valor, max_valor = intervalo
    for _ in range(bits):
        meio = (min_valor + max_valor) / 2
        if valor >= meio:
            resultado.append(1)
            min_valor = meio
        else:
            resultado.append(0)
            max_valor = meio
    return resultado

def gerar_bits_lat_lon(latitude, longitude, bits_total=30):
    bits_lon = dividir_intervalo(longitude, [-180.0, 180.0], bits_total // 2)
    bits_lat = dividir_intervalo(latitude, [-90.0, 90.0], bits_total // 2)

    bits_intercalados = []
    for lon_bit, lat_bit in zip(bits_lon, bits_lat):
        bits_intercalados.append(lon_bit)
        bits_intercalados.append(lat_bit)

    return bits_intercalados

def bits_para_geohash(bits):
    geohash = ""
    for i in range(0, len(bits), 5):
        grupo = bits[i:i + 5]
        if len(grupo) < 5:
            grupo += [0] * (5 - len(grupo))
        valor = 0
        for bit in grupo:
            valor = (valor << 1) | bit
        geohash += BASE32_GEOHASH[valor]
    return geohash

def gerar_geohash(lat, lon, precision):
    bits_total = precision * 5
    bits = gerar_bits_lat_lon(lat, lon, bits_total)
    return bits_para_geohash(bits)

def gerar_vizinhos(geohash_prefix):
    lat, lon = coordenadas_do_geohash(geohash_prefix)
    delta_lat = 0.045
    delta_lon = 0.045
    vizinhos = []
    for dlat in [-delta_lat, 0, delta_lat]:
        for dlon in [-delta_lon, 0, delta_lon]:
            nova_lat = lat + dlat
            nova_lon = lon + dlon
            novo_hash = gerar_geohash(nova_lat, nova_lon, precision=len(geohash_prefix))
            vizinhos.append(novo_hash)
    return sorted(set(vizinhos))
