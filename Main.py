try:
    from bs4 import BeautifulSoup
    import requests as rqt 
    import json 
    import sys
    import pygame  
    import os
    import threading
    import time
except ImportError:
    print("Please download all the libraries")
    
API_KEY = "YOUR API KEY"
PROJECT_TOKEN = "YOUR PROJECT TOKEN"
RUN_TOKEN = "YOUR RUN TOKEN"

pygame.init()

# Request access to the url and get the web's html
url = 'https://www.canada.ca/en/public-health/services/diseases/coronavirus-disease-covid-19.html'
request = rqt.get(url)
soup = BeautifulSoup(request.content, 'html.parser')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
			"api_key": self.api_key
		}
        self.data = self.get_data()
        self.txt_font = pygame.font.SysFont('Arial', 40)
    
    def get_data(self):
        request = rqt.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data = json.loads(request.text)
        return data 
    
    def get_total_cases(self):
        data = self.data['total']
        
        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']
    
    def get_deaths(self):
        data = self.data['total']
        
        for content in data:
            if content['name'] == "Deaths:":
                return content['value']
        
        return "0"
    
    def get_recover(self):
        data = self.data['total']
        
        for content in data:
            if content['name'] == "Recovered:":
                return content['value']
    
    def country_cases(self, country):
        data = self.data["country"]
        
        for content in data:
            if content['name'].lower() == country.lower():
                try:
                    return content['total_cases'], content['deaths'], content['tests'], content['recovers']
                except KeyError:
                    return content['total_cases'], "0", content['tests'], content['recovers']
    
    def update_data(self, screen):
        response = rqt.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
        txt = self.txt_font.render("Data updated successfully", True, BLACK)
        txt_rect = txt.get_rect(center=(400, 200))
        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    screen.blit(txt, txt_rect)
                    
                time.sleep(5)
                    
        t = threading.Thread(target=poll)
        t.start()
        
class CanadaTrack:
    def __init__(self, section):
        self.section = section
        self.get_case = self.section[0]
        self.cases = self.get_case.select_one('.mrgn-tp-md').text 


class Text:
    def __init__(self, screen):
        self.test = CanadaTrack(soup.findAll("section", {"class": "bg-success"}))
        self.confirm = CanadaTrack(soup.findAll("section", {"class": "bg-info"}))    
        self.death = CanadaTrack(soup.findAll("section", {"class": "bg-danger"}))  
        self.recover = CanadaTrack(soup.findAll("section", {"class": "bg-warning"}))  
        self.txt_font = pygame.font.SysFont('Arial', 24)
        self.screen = screen 
    
    def draw(self, txt, y):
        text = self.txt_font.render(txt, True, BLACK)
        text_rect = text.get_rect(center =(400, y))
        self.screen.blit(text, text_rect)
    
    def draw_font(self, txt, y, font):
        txt_font = pygame.font.SysFont('Arial', font)
        text = txt_font.render(txt, True, BLACK)
        text_rect = text.get_rect(center =(400, y))
        self.screen.blit(text, text_rect)
    
    def draw_adjust(self, txt, x, y, font):
        txt_font = pygame.font.SysFont('Arial', font)
        text = txt_font.render(txt, True, BLACK)
        text_rect = text.get_rect(center =(x, y))
        self.screen.blit(text, text_rect)

class button:
    def __init__(self, screen):
        self.screen = screen 
        self.txt_font = pygame.font.SysFont('Arial', 20)
    
    def draw(self, x, y, width, height, *txt):
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height))
        
        text = self.txt_font.render(txt[0], True, WHITE)
        text_rect = text.get_rect(center=(round(x + width/ 2), round(y + height/2)))
        self.screen.blit(text, text_rect)
            
    
    def hit_button(self, mouse_pos, x, y, width, height):
        mouse_x, mouse_y = mouse_pos
        
        if x < mouse_x < x + width:
            if y < mouse_y < y + height:
                return True 
        return False  

class Image:
    def __init__(self, screen):
        self.screen = screen
    
    def draw(self, img, y):
        img_rect = img.get_rect(center=(400, y))
        self.screen.blit(img, (img_rect))
    
    def draw_adjust(self, img, x, y):
        img_rect = img.get_rect(center=(x, y))
        self.screen.blit(img, (img_rect))
        
        
class Main:
    def __init__(self, WIDTH = 800, HEIGHT = 600):
        self.size = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode(self.size)
        self.text = Text(self.screen)
        self.button = button(self.screen)
        self.image = Image(self.screen)
        self.canada_img = pygame.image.load(os.path.join('Images', 'canada.png'))
        self.death_img = pygame.image.load(os.path.join('Images', 'danger.png'))
        self.confirm_img = pygame.image.load(os.path.join('Images', 'confirm.png'))
        self.test_img = pygame.image.load(os.path.join('Images', 'test.png'))
        self.recover_img = pygame.image.load(os.path.join('Images', 'heart.png'))
        self.globe = pygame.image.load(os.path.join('Images', 'globe.png'))
        self.images_list = [self.globe, self.death_img, self.confirm_img, self.test_img, self.recover_img]
        self.world_data = Data(API_KEY, PROJECT_TOKEN)
    
    def draw_button(self, pos, txt):
        if pos == "left":
            self.button.draw(0, 240, 200, 50, txt)
        elif pos == "right":
            self.button.draw(600, 240, 200, 50, txt)
        elif pos == "mid":
            self.button.draw(300, 550, 200, 50, txt)
        else:
            self.button.draw(300, 0, 200, 35, txt)
        
    def draw_text(self, confirm, death, test="Unknown", recover="Unknown"):
        y = 50
        self.text.draw("Number of people tested:", y)
        self.text.draw(test, y + 30)
        
        self.image.draw(self.confirm_img, y + 150 - 50)
        self.text.draw("Confirmed cases:", y + 150)
        self.text.draw(confirm, y + 180)
        
        self.image.draw(self.death_img, y + 300 - 50)
        self.text.draw("Death(s):", y + 300)
        self.text.draw(death, y + 330)
        
        self.image.draw(self.recover_img, y + 450 - 50)
        self.text.draw("Recover(s):", y + 450)
        self.text.draw(recover, y + 480)
    
    def draw_table(self):
        rows = 6
        columns = 8
        
        x = 50
        y = 130
        
        for i in range(rows):
            pygame.draw.line(self.screen, BLACK, (x, 50), (x, 550), 3)
            x += 140
        
        #First horizontal line
        pygame.draw.line(self.screen, BLACK, (50, 50), (750, 50), 3)
        for i in range(columns):
            pygame.draw.line(self.screen, BLACK, (50, y), (750, y), 3)
            y += 60
    
    def table_content(self):
        BRAZIL = self.world_data.country_cases('Brazil')
        RUSSIA = self.world_data.country_cases('Russia')
        INDIA = self.world_data.country_cases('India')
        UK = self.world_data.country_cases('UK')
        SPAIN = self.world_data.country_cases('Spain')
        CHINA = self.world_data.country_cases('China')
        VIETNAM = self.world_data.country_cases('Vietnam')
        
        countries_list = [BRAZIL, RUSSIA, INDIA, UK, SPAIN, CHINA, VIETNAM]
        countries_list_string = ["Brazil", "Russia", "India", "UK", "Spain", "China", "Vietnam"]
        x = 260
        y = 160
        #Displaying data inside table
        for rows in range(7):
            for columns in range(4):
                self.text.draw_adjust(countries_list[rows][columns], x, y, 20)
                x += 140
            x = 260
            y += 60
        
        #Displaying countries:
        c_y = 160
        for countries in countries_list_string:
            self.text.draw_adjust(countries, 120, c_y, 20)
            c_y += 60
            
        #Displaying image 
        i_x = 120
        for img in self.images_list:
            self.image.draw_adjust(img, i_x, 90)
            i_x += 140
        
    
    def updating_data(self):
        updating = True
        while True:
            self.screen.fill(WHITE)
            try:
                self.world_data.update_data(self.screen)
                self.text.draw_font("Please wait, this progress might take a while", 270, 25)
            except:
                self.text.draw_font("There's something wrong, please restart the program", 200, 40)
    
            self.text.draw_font("Restart the program after this to see changes", 450, 25)
            self.text.draw_font("Press any key to go back", 350, 60)
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   
                    sys.exit()
                    pygame.quit()
    
                if event.type == pygame.KEYDOWN:
                    self.canada()
                    break
    
            pygame.display.update()
            
    def canada(self):
        while True:
            self.screen.fill(WHITE)
            self.screen.blit(self.canada_img, (600, 100))
            self.screen.blit(self.canada_img, (200 - self.canada_img.get_width(), 100))
            self.draw_text(self.text.confirm.cases, self.text.death.cases, self.text.test.cases, self.text.recover.cases)
            self.draw_button("left", "<<< USA")
            self.draw_button("right", "Worldwide >>>")
            self.draw_button("mid", "Countries List")
            self.draw_button("top", "Update Data")
            
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                
                if event.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button.hit_button(mouse_pos, 600, 240, 200, 50):
                        self.worldwide()
                        break
                    elif self.button.hit_button(mouse_pos, 0, 240, 200, 50):
                        self.usa()
                    elif self.button.hit_button(mouse_pos, 300, 550, 200, 50):
                        self.countries()
                    elif self.button.hit_button(mouse_pos, 300, 0, 200, 35):
                        self.updating_data()
                    
            pygame.display.update()
    
    def countries(self):
        while True:
            self.screen.fill(WHITE)
            self.draw_button("top", "^^ Canada ^^")
            self.draw_table()
            self.table_content()
            
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                
                if event.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button.hit_button(mouse_pos, 300, 0, 200, 35):
                        self.canada()
                    
            pygame.display.update()
        
    
    def worldwide(self):
        while True:
            self.screen.fill(WHITE)
            self.draw_text(self.world_data.get_total_cases(), self.world_data.get_deaths(), recover=self.world_data.get_recover())
            self.draw_button("left", "<<< Canada")
            
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                
                if event.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button.hit_button(mouse_pos, 0, 240, 200, 50):
                        self.canada()
                    
            pygame.display.update()
    
    def usa(self):
        while True:
            usa_data = self.world_data.country_cases("USA")
            self.screen.fill(WHITE)
            self.draw_text(usa_data[0], usa_data[1], usa_data[2], usa_data[3])
            self.draw_button("right", "Canada >>>")
            
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                
                if event.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button.hit_button(mouse_pos, 600, 240, 200, 50):
                        self.canada()
                    
            pygame.display.update()

if __name__ == "__main__":
    main = Main()
    main.canada()
