/********************************************************** 
ATOM_LIGHT : ArTificial Open Market

Semi short version 2
All in one file, all is public, one orderbook, agents,
We add now notification for agents and validation time

Author  : P Mathieu, O Brandouy, Univ Lille1, France
Email   : philippe.mathieu@lifl.fr
Address : Philippe MATHIEU, LIFL, UMR CNRS 8022, 
Lille 1 University
59655 Villeneuve d'Ascq Cedex, france
Date    : 14/12/2008


Amélioration fondamentale des performances : le carnet d'ordres
n'utilise plus un ArrayList mais un TreeSet. L'avantage est que
l'objet TreeSet garantit toujours une insertion en O(log(n)) et un
effacement en O(log(n)). On n'a plus à "retrier" à chaque tour !

Generate 100.000 tours de 2 agents. Result redirigé
TestAtomv2 : 1mn20
TestAtomv3 : 7sec   redirigé vers fichier
TestAtomv3 : 3,7sec redirigé vers /dev/null (sans valid)

C'est assez antinomique d'avoir un système qui réunit les 3 critères :
puissance en fontionalités, concision et densidé du code, rapidité
d'exécution. Il faut choisir !

Dans cette version une date de validité (en nombre de tours) est
ajoutée aux ordres. Elle sert uniquement dans l'approche Multi-agents
à comportement. Dans la boucle d'évaluation, les ordres trop anciens
sont détruits. La date de validité est relative; 3 signifie que
l'ordre restera actif durant 3 tours. Ceci permet maintenant de faire
un test interessant : laisser tourner ATOM sans arrêt avec un nombre
maxi d'ordres dans le carnet. Ce point est évidemment couteux en temps
! du coup je commente l'appel. Le ReplayEngine est maintenant
MultiAgents. On recrée exactement les mêmes agents que dans le fichier
initial. On a ici une propriété remarquable : un fichier généré est
rejoué à l'identique !

On ajoute aussi la notification d'execution d'un ordre à
l'agent. Quand un ordre est touché, l'agent concerné est informé (dans
tous les cas il fallait mettre à jour son portefeuille).  Question
fondamentale : que et comment notifier ??

Par contre, le ReplayOrder ne fonctionne qu'avec des validités
infinies, car ça ne passe pas par le decideOne de l'agent. Si on
voulait le faire, il faut mettre les #round dans le fichier

Un fichier de 26 agents lancés sur 100.000 tours
- passe 260.000 ordres
- fixe en moyenne 200.000 prix
- genere un fichier de ( 260.000 * 2 ) + (200.000 *3) lignes
le x2 parce que ordre + destroy ; le *3 parce que prix+repercussion
sur les 2 agents
- au total : 1.120.000 lignes ; grosso-modo 31Mo


Plot in R
x <- read.csv(file="toto",sep=";",header=FALSE)

avec ce fichier on peut ....
- tracer l'évolution des prix (courbe de prix)
y <- x[x[1]=="#Price",]
plot(y$V2,type="l") ou plot(x[1:1000,2],type="l")

- tracer la variation des prix

- tracer la courbe des quantités exécutées

- tracer la distribution de variations (histo))

- tracer d'évolution du cash d'un agent
z <- x[x[1]=="#Agent" & x[2]="paul",]
plot(z$V3,type="l")

- tracer d'évolution des actifs (wealth) d'un agent
z <- x[x[1]=="#Agent" & x[2]="paul",]
plot(z$V3+(z$V4*z$V5),type="l")

- la distribution du temps d'attente d'un ordre dans un carnet (Histo)





 ***********************************************************/

import java.util.*;
import java.io.*;

class LimitOrder
{
    public long id;       // unique, fait par le marché
    public String extId;  // exterieur, pour references et traces
    public long timestamp;// pour info car non unique, sinon remplacerait id
    public Agent sender;
    public char direction;
    public int quantity;
    private int initQuty;
    public long price;
    public long validity;
    public static final char ASK = 'A';
    public static final char BID = 'B';

    public LimitOrder(String extId,char direction, long price, int quantity, int validity)
    {
        this.extId = extId;
        this.direction = direction;
        this.quantity = quantity;
        this.initQuty = quantity;
        this.price = price;
	this.sender=null;
	this.validity = validity;
	this.id = -1; // not set at this time
    }

    public LimitOrder(String extId,char direction, long price, int quantity)
    {	this(extId,direction,price,quantity,-1);} // infinite life 
    
    public String toString()
    {	return ("Order;"+sender.name+";"+extId+";L;"+direction+";"+price+";"+quantity+";"+validity); }
}

//---------------------------------

class PriceRecord
{
    public long price;
    private int quantity;
    private char dir;
    private String extId1;
    private String extId2;
    
    public PriceRecord(long price, int quantity, char dir, String extId1, String extId2)
    {
	this.price = price;
	this.quantity = quantity;
	this.dir = dir;
	this.extId1 = extId1;
	this.extId2 = extId2;
    }

    public String toString()
    {	return price+";"+quantity+";"+dir+";"+extId1+";"+extId2;
    }
}

//---------------------------------

class Sort {

    public static final Comparator<LimitOrder> ASK = new Comparator<LimitOrder>() {
        public int compare(LimitOrder o1, LimitOrder o2) {
            if (o1.price == o2.price) {
                return (int) (o1.id - o2.id);
            }
            return (int) (o1.price - o2.price);
        }
    };
    public static final Comparator<LimitOrder> BID = new Comparator<LimitOrder>() {

        public int compare(LimitOrder o1, LimitOrder o2) {
            if (o1.price == o2.price) {
                return (int) (o1.id - o2.id);
            }
            return (int) (o2.price - o1.price);
        }
    };
}

//---------------------------------


class OrderBook
{
    public TreeSet<LimitOrder> ask;
    public TreeSet<LimitOrder> bid;
    public ArrayList<PriceRecord> lastPrices; 
    public long numberOfOrdersReceived;
    public long numberOfPricesFixed;
    private LimitOrder lastOrder;
    public PriceRecord lastFixedPrice;
    private static final int SHORT = 1;
    private static final int LONG = 2;
    private int logType = LONG;
   
    public OrderBook(){init();}

    void init()
    {
	ask = new TreeSet<LimitOrder>(Sort.ASK);
	bid = new TreeSet<LimitOrder>(Sort.BID);
	lastPrices = new  ArrayList<PriceRecord>();
        numberOfOrdersReceived=0;
        numberOfPricesFixed=0;
	lastOrder = null;
	lastFixedPrice = null;
    }

    public void setNewPrice(PriceRecord pc)
    {
	// lastPrices.add(pc);
	numberOfPricesFixed++;
	lastFixedPrice = pc;
	/* TRACE */ System.out.println("Price;"+pc);
	// System.out.println("Time;"+System.currentTimeMillis());
	// Il fixe plusieurs prix dans la meme milliseconde !!
    }


    void addOneOrder(LimitOrder lo)
    {
	if (lo.direction == LimitOrder.ASK)
	    {
		ask.add(lo);
		// Collections.sort(ask,Sort.ASK);
	    }
	else
	    {
		bid.add(lo);
		// Collections.sort(bid,Sort.BID);
	    }
    }

    void printState()
    {
        System.err.println("nb orders received  : " + numberOfOrdersReceived);
        System.err.println("nb fixed prices     : " + numberOfPricesFixed);
	System.err.println("leaving ask size    : " + ask.size());
	System.err.println("leaving bid size    : " + bid.size());
    }


    void send(LimitOrder lo)
    {
	int cumulQuty = 0;
        long localLastPrice = 0;
        LimitOrder older = null, newer = null;
	numberOfOrdersReceived++;
	lo.timestamp = System.currentTimeMillis();
	lo.id=numberOfOrdersReceived; // id unique géré manuellement car timestamp ne marche pas
	lastOrder = lo;

	/* TRACE */ System.out.println(lo);
	addOneOrder(lo);
	LimitOrder bask = (ask.isEmpty()?null:ask.first()); // ask.get(0));
	LimitOrder bbid = (bid.isEmpty()?null:bid.first()); // bid.get(0));
        while (!ask.isEmpty() && !bid.isEmpty()
	       && bask.price <= bbid.price) 
	    {
		// calcul du prix d'execution
		if (bask.id <= bbid.id) {
		    older = bask;
		    newer = bbid;
		} else {
		    older = bbid;
		    newer = bask;
		}
		long prixduplusancien = older.price;	
		
		// calcul de la quantite a executer
		int pluspetitequantite;
		if (bask.quantity <= bbid.quantity) {
		    pluspetitequantite = bask.quantity;
		} else {
		    pluspetitequantite = bbid.quantity;
		}
		
		long money = prixduplusancien * pluspetitequantite;
		
		// modify the two agents
		bbid.sender.cash -= money;
		bbid.sender.invest += pluspetitequantite;
		bask.sender.cash += money;
		bask.sender.invest -= pluspetitequantite;
		
		// mise a jour des ordres
		bbid.quantity-= pluspetitequantite;
		bask.quantity-= pluspetitequantite;
		
		localLastPrice = prixduplusancien;
		cumulQuty += pluspetitequantite;

		if (logType == LONG)
		    {
			PriceRecord pc = new PriceRecord(prixduplusancien, pluspetitequantite, newer.direction, bask.sender.name+"-"+bask.extId, bbid.sender.name+"-"+bbid.extId);
			setNewPrice(pc);
		    }

		// notification aux agents
		bbid.sender.touchedOrExecutedOrder(bbid);
		/* TRACE */ System.out.println("Agent;"+bbid.sender.name+";"+bbid.sender.cash+";"+bbid.sender.invest+";"+(lastFixedPrice!=null?lastFixedPrice.price:null));
		/* TRACE */ if (bbid.quantity==0) System.out.println("Exec;"+bbid.sender.name+"-"+bbid.extId);
		bask.sender.touchedOrExecutedOrder(bask);
		/* TRACE */ System.out.println("Agent;"+bask.sender.name+";"+bask.sender.cash+";"+bask.sender.invest+";"+(lastFixedPrice!=null?lastFixedPrice.price:null));
		/* TRACE */ if (bask.quantity==0) System.out.println("Exec;"+bask.sender.name+"-"+bask.extId);

		
		// Nettoyage eventuel
		if (bbid.quantity == 0) bid.pollFirst();     // bid.remove(bbid);
		if (bask.quantity == 0) ask.pollFirst();     // ask.remove(bask);
		bask = (ask.isEmpty()?null:ask.first());     // ask.get(0));
		bbid = (bid.isEmpty()?null:bid.first());     // bid.get(0));
	    }

	if (logType == SHORT)
	    {
		if (localLastPrice != -1 && cumulQuty !=0)
		    {
			PriceRecord pc = new PriceRecord(localLastPrice,cumulQuty,newer.direction,newer.sender.name+"-"+newer.extId,"-");
			setNewPrice(pc);
		    }

	    }
    }


    public String toString()
    {
	StringBuffer sb = new StringBuffer();
	sb.append("\n\n");
	for (Iterator<LimitOrder> it = ask.iterator(); it.hasNext();) {
	    sb.append(it.next()); sb.append("\n"); }
	sb.append("----------------\n");
	for (Iterator<LimitOrder> it = bid.iterator(); it.hasNext();) {
	    sb.append(it.next()); sb.append("\n"); }
	return sb.toString();
    }


    public void decreaseAndDeleteUnvalid() 
    {
	HashSet<LimitOrder> toRemove = new HashSet<LimitOrder>();
        for (Iterator<LimitOrder> it = ask.iterator(); it.hasNext();) 
	    {
		LimitOrder o = it.next();
		if (o.validity < 0) continue; // infinity
		o.validity--;
		// if (o.validity < 0) System.out.println("NEGATIF !!");
		if (o.validity == 0)
		    {
			toRemove.add(o);
			/* TRACE */ System.out.println("#Destroy;"+o.sender.name+"-"+o.extId);
		    }
	    }
	ask.removeAll(toRemove);

	toRemove = new HashSet<LimitOrder>();
	for (Iterator<LimitOrder> it = bid.iterator(); it.hasNext();) 
	    {
		LimitOrder o = it.next();
		if (o.validity < 0) continue; // infinity
		o.validity--;
		// if (o.validity < 0) System.out.println("NEGATIF !!");
		if (o.validity == 0)
		    {
			toRemove.add(o);
			/* TRACE */ System.out.println("#Destroy;"+o.sender.name+"-"+o.extId);
		    }
            }
	bid.removeAll(toRemove);
    }
}

//=======================================================

class MarketPlace
{
    public Map<String, Agent> agentList;
    public OrderBook ob;
    private long numberOfRounds;
    
    public MarketPlace(){init();}

    public void init()
    {
	agentList = new HashMap<String,Agent>();
	ob = new OrderBook();
	numberOfRounds=0;
    }

    void clear()
    {
	// on nettoie le carnet pour demarrer une nouvelle journée
	// par contre le numberOfRounds, numberOfOrdersReceived etc ne
	// sont pas réinitialisés.
	ob.ask.clear();
	ob.bid.clear();
    }

    public void addNewAgent(Agent a) 
    {
        a.market=this;
        agentList.put(a.name, a);	
    }

    void printState()
    {   // on ne passe que par market maintenant
	ob.printState();
    }

    void send(Agent a,LimitOrder lo)
    {   // on ne passe que par market maintenant
	lo.sender=a;
	ob.send(lo);
    }

    void runOnce()
    {
        numberOfRounds++;
	// ob.decreaseAndDeleteUnvalid(); // Comment to SpeeUp if validity = -1
	List<Agent> al = new ArrayList<Agent>(agentList.values());
        Collections.shuffle(al);
        for (Agent agent : al) 
	    {
		LimitOrder lo = agent.decide();
		if (lo !=null)
		    send(agent,lo);
	    }
	/* TRACE */ // System.out.println(ob);
	/* TRACE */ System.out.println("Tick;"+numberOfRounds+";"+ob.numberOfOrdersReceived);
    }
}

//-----------------------------------------

class Agent
{
    public String name;
    public long cash;
    public int invest;
    public MarketPlace market;
    private long myId;
    private long numberOfOrdersSent;

    public Agent(String name, long cash, int invest)
    {	init(name,cash,invest); }

    public Agent(String name, long cash)
    {	this(name,cash,0); }

    public Agent(String name)
    {	this(name,0,0); }

    public void init(String name, long cash, int invest)
    {
	this.name=name;
	this.cash=cash;
	this.invest=invest;
	myId=0;
	numberOfOrdersSent=0;
    }

    // utilisation d'un comportement. Retourne NULL ou un ordre
    LimitOrder decide()
    {
        long minPrice = 14000;
        long maxPrice = 15000;
        int minQuty   = 100;
        int maxQuty   = 1000;
	char dir = (Math.random()>0.5?LimitOrder.ASK:LimitOrder.BID);
	int quty = minQuty + (int) (Math.random() * (maxQuty - minQuty));
	long price = minPrice + (int) (Math.random() * (maxPrice - minPrice));
	myId+=10;
	numberOfOrdersSent++;

	return new LimitOrder(""+myId,dir,price,quty,5); 
	// Orders will not stay more than 5 ticks
    }

    public void touchedOrExecutedOrder(LimitOrder o)
    {
	// NOTIFICATION : do what you want
    }
}


//=======================================================

public class TestATOMv3
{
    public static void main(String args[])
    {
	// COMMENT FAIRE UN GENERATE ENGINE

	MarketPlace m = new MarketPlace();
	m.addNewAgent(new Agent("paul",100000));
	m.addNewAgent(new Agent("pierre",100000));
	for (int i=1;i<=100000;i++) m.runOnce();
	m.printState();
    }
}

//-----------------------------------------

class TestATOMv3b
{
    public static void main(String args[]) throws Exception
    {
	// COMMENT FAIRE UN REPLAY ENGINE MultiAgent	

	MarketPlace m = new MarketPlace();
	Agent a;
	String line;
	BufferedReader file = new BufferedReader(new FileReader(args[0]));
	StringTokenizer st;
	while ((line = file.readLine()) != null)
	    {   if ("#!/ ".contains(""+line.charAt(0))) continue;

		st = new StringTokenizer(line,";");
		while(st.hasMoreElements())
		    {
			String agentName = ((String)st.nextElement()); // inutile
		       
			a = m.agentList.get(agentName);
			if (a==null) { a= new Agent(agentName,0); m.addNewAgent(a);}

			String extId = ((String)st.nextElement());
			char type = ((String)st.nextElement()).charAt(0);
			char dir = ((String)st.nextElement()).charAt(0);
			long price = Integer.parseInt((String)st.nextElement());
			int quty = Integer.parseInt((String)st.nextElement());
			// int valid = Integer.parseInt((String)st.nextElement());
			m.send(a,new LimitOrder(extId,dir,price,quty));
		    }
		// System.out.print(line + "\t-> ok "+dir);
	    }
	m.printState();
    }
}
 
//---------------------------------

class TestATOMv3c
{
    public static void main(String args[])
    {
	// COMMENT FAIRE SA PROPRE EXPERIENCE

	MarketPlace m = new MarketPlace();
	Agent a = new Agent("paul",0);
	m.addNewAgent(a); // inutile ici

	LimitOrder orders[] =
	    {
		new LimitOrder("a",LimitOrder.BID, (long) 100, 50),
		new LimitOrder("b",LimitOrder.BID, (long) 110, 30),
		new LimitOrder("c",LimitOrder.ASK, (long) 150, 10),
		new LimitOrder("d",LimitOrder.ASK, (long) 130, 20),
		new LimitOrder("e",LimitOrder.BID, (long) 135, 35),
		new LimitOrder("f",LimitOrder.ASK, (long) 100, 100)
	    };
	
        for (int i = 0; i < orders.length; i++)
            m.send(a,orders[i]);
	
	/* A la fin, 2 ask, 0 bid, 4 prix fixés : 130(20) 135(15) 110(30) 100(50) */
	m.printState();
    }
}

