import wuy

class helloWorld(wuy.Window):
    """ <button onclick="wuy.beep()">BEEP</button> 
    <input type="file" name="myFile" onselect="wuy.select()">

"""
    size=(100,100)

    def beep(self):
        print("\a BEEP !!!")

    def select(self):
        print("SELECT")

        
helloWorld()
