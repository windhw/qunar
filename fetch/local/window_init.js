var window = new Object;
window.closed        	 = false; //Returns a Boolean value indicating whether a window has been closed or not
window.defaultStatus 	 = '';    //Sets or returns the default text in the statusbar of a window
window.frames 	         = window ;//Returns an array of all the frames (including iframes) in the current window
window.innerHeight 	= 866;  //Returns the inner height of a window's content area
window.innerWidth       = 1280;	//Returns the inner width of a window's content area
window.length 	        = 0;    //Returns the number of frames (including iframes) in a window
window.name 	        = "";    //Sets or returns the name of a window
window.opener 	        = null ;  //Returns a reference to the window that created the window
window.outerHeight 	= 994; //Returns the outer height of a window, including toolbars/scrollbars
window.outerWidth 	= 1280; //Returns the outer width of a window, including toolbars/scrollbars
window.pageXOffset 	= 0 ;    //Returns the pixels the current document has been scrolled (horizontally) from the upper left corner of the window
window.pageYOffset 	= 0 ; //Returns the pixels the current document has been scrolled (vertically) from the upper left corner of the window
window.screenLeft 	= 0 ; //Returns the x coordinate of the window relative to the screen
window.screenTop 	= 0 ; //Returns the y coordinate of the window relative to the screen
window.screenX 	        = 0 ; //Returns the x coordinate of the window relative to the screen
window.screenY 	        = 0 ; //Returns the y coordinate of the window relative to the screen
window.status 	        = ""; //Sets or returns the text in the statusbar of a window
window.top 	        = window ; //Returns the topmost browser window
//window.location.hash ""
//window.location.host "wuti.tk"
//window.location.hostname "wuti.tk"
//window.location.href "http://wuti.tk/msg?a=b"
//window.location.origin "http://wuti.tk"
//window.location.pathname "/msg"
//window.location.protocol "http:"
window.location 	= new Object; //Returns the Location object for the window (See Location object)
    window.location.hash      = '';
    window.location.host      = '';
    window.location.hostname  = '';
    window.location.href      = '';
    window.location.origin    = '';
    window.location.pathname  = '';
    window.location.port      = '';
    window.location.protocol  = '';

window.navigator        = {
    appCodeName: "Mozilla" ,
    appName: "Netscape" ,
    appVersion: "5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36" ,
    cookieEnabled: true ,
    doNotTrack: null ,
    hardwareConcurrency: 2 ,
    language: "zh-CN" ,
    languages: {0: "zh-CN" , 1: "zh" , 2: "en"} ,
    maxTouchPoints: 0 ,
    onLine: true ,
    platform: "Win32" ,
    product: "Gecko" ,
    productSub: "20030107" ,
    userAgent: "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36" , 
    vendor: "Google Inc." ,
    vendorSub: "" }; 
window.history 	        = {length: 4 , state: null };// new Object;  //Returns the History object for the window (See History object)
window.parent 	        = window;  //Returns the parent window of the current window
window.screen 	        = {availHeight: 994 ,
	                   availLeft: 0 ,
			   availTop: 0 ,
			   availWidth: 1280,
			   colorDepth: 24,
			   height: 1024,
			   pixelDepth: 24, 
			   width: 1280 };  //Returns the Screen object for the window (See Screen object)
window.document         = {URL: '' , 
	                   cookie: ''};  //Returns the Document object for the window (See Document object)
document = window.document
window.String = String
