import customtkinter as CTK

class SCTkButton(CTK.CTkButton):
    def __init__(self, master=None,theme=0,style=0, **kwargs):
        super().__init__(master, **kwargs)
        self.style=style
        self.theme=theme
        self.common_setup()
        self.customize_widget()
    
    def common_setup(self):
        match self.theme:
            case 0: 
                self. common_setup_t0()
            case 1:
                self. common_setup_t1()
   
      
    def common_setup_t0(self):
        main_font = CTK.CTkFont(family="Helvetica", size=12)
        self.configure(hover=True, font=main_font,height=40, width=120, border_width=2, corner_radius=5,bg_color="#262626", text="Button Theme "+ str(self.theme)+" st"+str(self.style))
        
    def common_setup_t1(self):
        main_font = CTK.CTkFont(family="Helvetica", size=12)
        self.configure(hover=True, font=main_font,        hover_color= "black", bg_color="#262626",
        fg_color= "#262626",height=40,width= 120,border_width=2,corner_radius=3,text="Button Theme "+ str(self.theme)+" st"+str(self.style))        
    
    def customize_widget(self):
        match self.theme:
            case 0: 
                self.customize_widget_t0()
            case 1:
                self.customize_widget_t1()
    
 
    def customize_widget_t0(self):
        if self.style == 0:
            self.configure(text_color="#363636")
        else:
           self.configure(text_color="white" )   
                    
        match self.style:
            case 0:
                self.configure(hover_color= "#f2f2f2",border_color= "#d3d3d3", fg_color= "#fafafa")
            case 1:
                self.configure( hover_color= "#050505",  border_color= "#2d6f9e",fg_color= "#3b8cc6")
            case 2:
                self.configure( hover_color= "#6fb9d5",border_color= "#528aa0",fg_color= "#68aec9")
            case 3:
                self.configure(hover_color= "#81b867",border_color= "#608a4d",fg_color= "#79ae61")
                
            case 4:    
                self.configure(hover_color= "#ffb557",border_color= "#bc863f",fg_color= "#eda850")
                
            case 5:
                self.configure(hover_color= "#e06a61",  border_color= "#9e4a43",fg_color= "#c75d55")
                
            case 6: 
                self.configure(hover_color= "#454545",border_color= "#161616", fg_color= "#363636")
                
    def customize_widget_t1(self):
                    
        match self.style:
            case 0:
                self.configure(text_color="white",border_color= "#d3d3d3",) 
            case 1:
                self.configure(   text_color="#3b8cc6",border_color= "#3b8cc6",  )
            case 2:
                self.configure( text_color="#68aec9",border_color= "#68aec9",  )
            case 3:
                self.configure(text_color="#79ae61",border_color= "#79ae61", )
                
            case 4:    
                self.configure(text_color="#eda850",border_color= "#eda850", )
                
            case 5:
                self.configure(text_color="#c75d55",border_color= "#c75d55", )
                
            case 6: 
                self.configure(text_color="white",border_color= "black", )                
 


def main():
    main_window = CTK.CTk()
    main_window.title("ButtonsTemplates")
    main_window.geometry("980x160+200+50")
    main_window.configure(bg="#262626")
    buttons=[[]]
    
    for i in range(2):
        for j in range(7):
            button = SCTkButton(main_window,theme=i, style=j)
            button.grid(row=i, column=j, padx=10, pady=20)
            buttons[i].append(button)
        buttons.append([])    
    main_window.mainloop()


if __name__ == "__main__":
   main()