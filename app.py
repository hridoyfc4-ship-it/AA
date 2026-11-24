import os, time, json, requests, urllib3
from Crypto.Cipher import AES
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAIN_KEY = 'Yg&tc%DEuh6%Zc^8'.encode("utf-8")
MAIN_IV = '6oyZDr22E3ychjM%'.encode("utf-8")

def vr(n):
 d=[]
 while True:
  b=n&0x7F;n>>=7
  if n:b|=0x80
  d.append(b)
  if not n:break
 return bytes(d)

def pb(F):
 p=bytearray()
 for f,v in F.items():
  if isinstance(v,bool):p.extend(vr((f<<3)|0));p.extend(vr(1 if v else 0))
  elif isinstance(v,int):p.extend(vr((f<<3)|0));p.extend(vr(v))
  elif isinstance(v,str):d=v.encode();p.extend(vr((f<<3)|2));p.extend(vr(len(d)));p.extend(d)
  elif isinstance(v,(bytes,bytearray)):d=bytes(v);p.extend(vr((f<<3)|2));p.extend(vr(len(d)));p.extend(d)
 return bytes(p)

def rv(data,pos):
 r=0;s=0
 while pos<len(data):
  b=data[pos];pos+=1;r|=(b&0x7F)<<s
  if not(b&0x80):break
  s+=7
 return r,pos

def parse(data):
 f={};pos=0;n=len(data)
 while pos<n:
  try:k,pos=rv(data,pos)
  except:break
  fn=k>>3;wt=k&7
  try:
   if wt==0:v,pos=rv(data,pos)
   elif wt==2:ln,pos=rv(data,pos);v=data[pos:pos+ln];pos+=ln
   elif wt==5:v=data[pos:pos+4];pos+=4
   elif wt==1:v=data[pos:pos+8];pos+=8
   else:break
  except:break
  f.setdefault(fn,[]).append(v)
 return f

def enc(k,i,p):
 pl=16-(len(p)%16)
 return AES.new(k,AES.MODE_CBC,i).encrypt(p+bytes([pl]*pl))

def dec(k,i,c):
 d=AES.new(k,AES.MODE_CBC,i).decrypt(c)
 pl=d[-1]
 if 1<=pl<=16:d=d[:-pl]
 return d

def strip_prefix(b):
 if len(b)<=64:return b
 try:
  if 8 in parse(b):return b
 except:pass
 try:
  if 8 in parse(b[64:]):return b[64:]
 except:pass
 return b[64:]

def oauth(uid,pwd):
 url="https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
 H={"User-Agent":"GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)","Content-Type":"application/json; charset=utf-8"}
 try:
  R=requests.post(url,headers=H,json={"client_id":100067,"client_secret":'2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3',"client_type":2,"device_id":"","password":pwd,"response_type":"token","uid":int(uid)},verify=True,timeout=20)
 except Exception as e:
  print(f"oauth err: {e}");return None
 if R.status_code not in(200,201):
  print(f"oauth HTTP {R.status_code}");return None
 J=R.json()
 if J.get("code")!=0:
  print(f"oauth code={J.get('code')}");return None
 d=J.get("data",{})
 return {"access_token":d.get("access_token"),"open_id":d.get("open_id")}

def build_login_payload(at,oi):
 P={}
 P[3]=time.strftime("%Y-%m-%d %H:%M:%S");P[4]="free fire";P[5]=1;P[7]="1.132.9"
 P[8]="Android OS 14 / API-34 (UP1A.231005.007/V816.0.15.0.UNQMIXM)"
 P[9]="Handheld";P[10]="Grameenphone";P[11]="CarrierDataNetwork"
 P[12]=1666;P[13]=750;P[14]="352";P[15]="ARM64 FP ASIMD AES | 2400 | 8"
 P[16]=5563;P[17]="Mali-G57 MC2"
 P[18]="OpenGL ES 3.2 v1.r32p1-01eac0.0a0b917d9265b4c01be9925306306139"
 P[19]="Google|9cc73f7a-91f6-40f6-87ec-5b67e597eb8c";P[20]="59.152.5.188"
 P[21]="en";P[22]=oi;P[23]="8";P[24]="Handheld"
 P[25]="Xiaomi 2312DRAABI";P[26]="BD";P[29]=at;P[30]=1
 P[41]="Grameenphone";P[42]="Cellular"
 P[57]="7428b253defc164018c604a1ebbfebdf"
 P[60]=109685;P[61]=58294;P[62]=797;P[63]=18000;P[64]=58818;P[65]=109685
 P[66]=58818;P[67]=109685;P[73]=2
 P[74]="/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/lib/arm64"
 P[76]=1
 P[77]="b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/base.apk"
 P[78]=3;P[79]=2;P[81]="64";P[83]="2019121229";P[85]=3;P[86]="OpenGLES2"
 P[87]=4095;P[88]=8
 P[89]=b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
 P[90]="Dhaka";P[91]="C";P[92]=8043;P[93]="android"
 P[94]="KqsHT4XbSZhqerDNUhjbS3DxG/4+I62zQU2tZFJN91kBUICAlZ5yujshLKvjlk/KiShfKfis8EeB1PMhFHIodWPncZC4fCHYF3TcTwNj95aWY/S3"
 P[95]=111207;P[96]='{"cur_rate":[60,90,120],"support_etc2":false}'
 P[97]=1;P[98]=1;P[99]="4";P[100]="4";P[102]="GQ]        e";P[103]=1
 P[104]=45174;P[105]=1
 P[106]="https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a"
 P[107]="1.9393e7b8e53e8aeb"
 return enc(MAIN_KEY,MAIN_IV,pb(P))

def major_login(payload):
 url="https://loginbp.ppmainecoonghj.com/MajorLogin"
 H={"User-Agent":"UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)","Accept":"*/*","Accept-Encoding":"deflate, gzip","X-GA-SV":str(int(time.time())),"Authorization":"Bearer ","X-GA":"v1 1","ReleaseVersion":"OB55","Content-Type":"application/x-www-form-urlencoded","X-Unity-Version":"2018.4.12f1"}
 try:
  R=requests.post(url,headers=H,data=payload,verify=True,timeout=20)
 except Exception as e:
  print(f"majorlogin err: {e}");return None
 if R.status_code not in(200,201) or not R.content:
  print(f"majorlogin HTTP {R.status_code}");return None
 return R.content

def getv(f,n):
 v=f.get(n)
 if v is None:return None
 if isinstance(v,list):v=v[0]
 return v

def extract(ml):
 body=strip_prefix(ml);f=parse(body)
 jwt_b=getv(f,8);url_b=getv(f,10);key_b=getv(f,22);iv_b=getv(f,23)
 jwt=jwt_b.decode() if isinstance(jwt_b,bytes) else jwt_b
 url=url_b.decode() if isinstance(url_b,bytes) else url_b
 if not jwt or not isinstance(key_b,bytes) or not isinstance(iv_b,bytes):
  print("ml parse failed");return None
 return {"jwt":jwt,"url":url}

def smart_decode(raw_bytes):
 try:
  f=parse(raw_bytes)
  if 1 in f and isinstance(f[1],list) and f[1]:
   return f,"raw_protobuf"
 except:pass
 for skip in (0,16,32,64):
  try:
   body=raw_bytes[skip:]
   if len(body)%16!=0:continue
   f=parse(dec(MAIN_KEY,MAIN_IV,body))
   if 1 in f:return f,f"aes_skip_{skip}"
  except:pass
 for skip in (16,32,64):
  try:
   f=parse(raw_bytes[skip:])
   if 1 in f:return f,f"raw_skip_{skip}"
  except:pass
 return None,"failed"

def get_player(uid,jwt,server):
 payload=pb({1:int(uid),2:7})
 data_enc=enc(MAIN_KEY,MAIN_IV,payload)
 H={"User-Agent":"UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)","Accept":"*/*","Accept-Encoding":"deflate, gzip","X-GA-SV":str(int(time.time())),"Authorization":f"Bearer {jwt}","X-GA":"v1 1","ReleaseVersion":"OB55","Content-Type":"application/x-www-form-urlencoded","X-Unity-Version":"2018.4.12f1"}
 R=requests.post(server+"/GetPlayerPersonalShow",data=data_enc,headers=H,timeout=20,verify=True)
 if R.status_code!=200:
  raise Exception(f"HTTP {R.status_code}: {R.text[:200]}")
 print(f"Response len={len(R.content)} | first_hex={R.content[:32].hex()}")
 raw,method=smart_decode(R.content)
 print(f"Decode method: {method}")
 if not raw:
  print(f"Hex dump: {R.content.hex()[:300]}")
  raise Exception("all decode attempts failed")
 return raw

def g(d,k):
 if not isinstance(d,dict):return None
 v=d.get(k)
 if isinstance(v,list):v=v[0] if v else None
 if isinstance(v,bytes):
  try:return v.decode()
  except:return v.hex()
 return v

def sub(fields,k):
 v=fields.get(k)
 if not v:return {}
 v=v[0]
 if isinstance(v,bytes):return parse(v)
 return v if isinstance(v,dict) else {}

def sanitize(o):
 if isinstance(o,bytes):
  try:return o.decode()
  except:return o.hex()
 if isinstance(o,dict):return {k:sanitize(v) for k,v in o.items()}
 if isinstance(o,list):return [sanitize(v) for v in o]
 return o


from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
allowed_origin = os.environ.get("ALLOWED_ORIGIN", "")
CORS(app, resources={r"/api/*": {"origins": [x.strip() for x in allowed_origin.split(",") if x.strip()]}})

def config_error():
    if len(MAIN_KEY) != 16 or len(MAIN_IV) != 16:
        return "GAR_MAIN_KEY and GAR_MAIN_IV must each be 16 characters."
    return None

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "FF INSIGHT API"})

@app.route("/api/player", methods=["POST", "OPTIONS"])
def player_lookup():
    if request.method == "OPTIONS":
        return ("", 204)
    problem = config_error()
    if problem:
        return jsonify({"error": problem}), 500

    body = request.get_json(silent=True) or {}
    uid = str(body.get("uid", "")).strip()
    if not uid.isdigit() or not (5 <= len(uid) <= 20):
        return jsonify({"error": "Enter a valid numeric Free Fire UID (5–20 digits)."}), 400

    try:
        acc = oauth('8494306217', '2E8700D3F5FBDAAFA0C46BCDB6EB559BE29A513AAB4AE57F6A93186A015B13AA')
        if not acc:
            return jsonify({"error": "Garena guest OAuth failed. Check credentials or API availability."}), 502

        ml = major_login(build_login_payload(acc["access_token"], acc["open_id"]))
        if not ml:
            return jsonify({"error": "Garena MajorLogin failed. The game endpoint may have changed."}), 502

        ad = extract(ml)
        if not ad:
            return jsonify({"error": "Could not decode the login response."}), 502

        server = ad["url"] or "https://clientbp.ppmainecoonghj.com"
        if not server.startswith("http"):
            server = "https://" + server

        raw = get_player(uid, ad["jwt"], server)
        bi = sub(raw, 1)
        pi = sub(raw, 2)
        ci = sub(raw, 6)
        pet = sub(raw, 8)
        soc = sub(raw, 9)
        cred = sub(raw, 11)

        out = {
          "AccountInfo": {
            "AccountAvatarId": g(bi,12), "AccountBPBadges": g(bi,18),
            "AccountBPID": g(bi,19), "AccountBannerId": g(bi,11),
            "AccountCreateTime": g(bi,44), "AccountEXP": g(bi,7),
            "AccountLastLogin": g(bi,24), "AccountLevel": g(bi,6),
            "AccountLikes": g(bi,21), "AccountName": g(bi,3),
            "AccountRegion": g(bi,5), "AccountSeasonId": g(bi,20),
            "AccountType": g(bi,2), "BrMaxRank": g(bi,35),
            "BrRankPoint": g(bi,15), "CsMaxRank": g(bi,36),
            "CsRankPoint": g(bi,31),
            "EquippedWeapon": bi.get(32, []) if isinstance(bi.get(32), list) else [],
            "ReleaseVersion": g(bi,50), "ShowBrRank": g(bi,52),
            "ShowCsRank": g(bi,53), "Title": g(bi,48)
          },
          "AccountProfileInfo": {
            "EquippedOutfit": pi.get(4, []) if isinstance(pi.get(4), list) else [],
            "EquippedSkills": pi.get(5, []) if isinstance(pi.get(5), list) else []
          },
          "GuildInfo": {
            "GuildCapacity": g(ci,5), "GuildID": str(g(ci,1)),
            "GuildLevel": g(ci,4), "GuildMember": g(ci,6),
            "GuildName": g(ci,2), "GuildOwner": str(g(ci,3))
          },
          "PetInfo": {"PetId":g(pet,1),"PetName":g(pet,2),"PetLevel":g(pet,3),"PetExp":g(pet,4)},
          "SocialInfo": {"Signature":g(soc,9),"Language":g(soc,3),"Gender":g(soc,2)},
          "CreditScoreInfo": {"CreditScore":g(cred,1),"RewardState":g(cred,3)}
        }
        return jsonify(sanitize(out))
    except Exception as exc:
        # Return a generic error; detailed exceptions are kept out of public responses.
        app.logger.exception("UID lookup failed")
        return jsonify({"error": "Lookup failed. The Garena endpoint/protocol may have changed; check hosting logs."}), 502
