# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con

def findAirlinebyAge(x,y):
    
    # Create a new connection
    # Create a new connection
    con=connection()
    minYear = 2022 - int(x) 
    maxYear = 2022 - int(y)
    if int(x) < int(y):
        return [("Age X must be greated than Y",)]
    results = [("airline_name","num_of_passengers", "num_of_aircrafts"), ]
 

    sql = f"""
    select a.name , count(distinct p.id) , count(distinct air.id)
    from airlines a , routes r , flights f , flights_has_passengers fp , passengers p , airplanes air , airlines_has_airplanes aha
    where r.airlines_id = a.id and f.routes_id = r.id and fp.flights_id = f.id and 
    fp.passengers_id = p.id and p.year_of_birth > {minYear} and p.year_of_birth < {maxYear} and aha.airlines_id = a.id and air.id = aha.airplanes_id
    group by a.name 
    order by count(distinct p.id) desc;
    """
    # Create a cursor on the connection
    cur=con.cursor()
    cur.execute(sql)
    results.append(cur.fetchone())

    return results


def findAirportVisitors(x,a,b):
    
   # Create a new connection
    con=connection()
    results = [("aiport_name", "number_of_visitors"),]
    sql = f"""
            select a.name , count(p.id)
            from airports a , routes r , flights f ,flights_has_passengers fp , passengers p , airlines air
            where r.destination_id = a.id and f.routes_id = r.id and fp.flights_id = f.id and fp.passengers_id = p.id 
            and f.date >= "{a}" and f.date < "{b}" and air.name = "{x}" and r.airlines_id = air.id
            group by a.name
            order by count(p.id) desc;

        """
    
    # Create a cursor on the connection
    cur=con.cursor()
    cur.execute(sql)
    data = cur.fetchall()

    for row in data:
        results.append(row)

    return results

def findFlights(x,a,b):

    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()   
   
    # if alias is null return the name of the airline

    sql = f"""   
            SELECT f.id , a.alias , air2.name , ap.model
            FROM flights f , routes r , airlines a , airplanes ap, airports air1 , airports air2 
            WHERE  a.active = 'Y' and r.airlines_id = a.id and air1.id = r.source_id and air2.id = r.destination_id and air1.city = "{a}" and air2.city = "{b}"
            and f.routes_id = r.id and ap.id = f.airplanes_id and f.date = "{x}" 
            and a.alias IS NOT NULL
            UNION
            SELECT f.id , a.name , air2.name , ap.model
            FROM flights f , routes r , airlines a , airplanes ap, airports air1 , airports air2 
            WHERE  a.active = 'Y' and r.airlines_id = a.id and air1.id = r.source_id and air2.id = r.destination_id and air1.city = "{a}" and air2.city = "{b}"
            and f.routes_id = r.id and ap.id = f.airplanes_id and f.date = "{x}"        
           
            
          """
    cur.execute(sql)

    data = cur.fetchall()
    
    result = [("flight_id", "alt_name", "dest_name", "aircraft_model"),]
    for row in data:
        result.append(row)    
    return result
    

def findLargestAirlines(N):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    result = [("name", "id", "num_of_aircrafts", "num_of_flights"),]
    cur=con.cursor()
    sql = """ 
            SELECT a.name, a.id ,count(distinct air.number), count(*) FROM airlines a , flights f , airplanes air , routes r
            WHERE f.routes_id = r.id and a.id = r.airlines_id and f.airplanes_id = air.id
            GROUP BY a.id 
            ORDER BY count(f.id) desc

          """   

    cur.execute(sql)
    i = 0 
    if N == "" or N=='0':
        return [("You did not enter a number or you entered 0!",)]
    else:
        while i < int(N):
            current = cur.fetchone()
            result.append(current)
            min = current[3]            
            i+=1
    last = cur.fetchone()
    if last[3] == min : # eipate se mia erotisi ama iparxei isopalia na bgalei kai tin epomeni eteria akoma kai an einai >N
        result.append(last)
    return result
    
def insertNewRoute(x,y):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()
    def checkifInside(d):
        sql = f"""
        select a.alias from airlines a
        """
        cur.execute(sql)
        data = cur.fetchall()
        for row in data:
            if row[0] == x:
                return True
        
        return False  
    

    if not checkifInside(x):
        return (["Try different alias"],)

    sql1 = """select airports.id from airports
                where airports.id not in (select routes.destination_id
                from routes, airports, airlines
                where airlines.id = routes.airlines_id
                and airports.id = routes.source_id
                and airports.name = '%s'
                and airlines.alias = '%s')""" % (y,x)
    cur.execute(sql1)
    dest_id = cur.fetchone()
    dest_id = dest_id[0] #!

    sql2 = f"""select airports.id from airports
                where airports.name = "{y}" """ 
    cur.execute(sql2)
    sourceid =  cur.fetchone()
    
    sourceid = sourceid[0] #!

    sql3 = """select airlines.id from airlines
                where airlines.alias = '%s' """ % (x)
    cur.execute(sql3)
    airl_id = cur.fetchone()
    airl_id = airl_id[0] #!   
    
    sql4 = f"""
        select r.id from routes r , airlines a 
        where r.airlines_id = a.id and a.alias = "{x}"
    """
    cur.execute(sql4)
    routeIDs = cur.fetchall()
    maxRouteID = max(routeIDs)
    new_id = maxRouteID[0]+1

    

    cur.execute("insert into routes(id,airlines_id,source_id,destination_id) values (%d,%d,%d,%d)"%(new_id,airl_id,sourceid,dest_id))
    try:
        con.commit()
        return [("result",),("OK",)]
    except:
        con.rollback()
    return [("insertion failed",)]
