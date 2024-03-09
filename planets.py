import pygame,math,copy,threading
pygame.init()

width,height = 1500,750
WIN = pygame.display.set_mode((width,height))
pygame.display.set_caption("Planet Simulator")

font = pygame.font.SysFont('Comic Sans MS', 14)

AU = 149.6e6 * 1000
G = 6.67428e-11
SCALE = 250 / AU
TIMESTEP = (3600*24)*10

GRAY = (22,50,79)
YELLOW = (255,255,0)
ORANGE = (213,133,18)
BLUE = (30,144,255)
RED = (255,0,0)
WHITE = (255,255,255)

class Game:
    def __init__(self):
        self.bodies = []
        self.buttons = []
        self.mouse = pygame.mouse.get_pos()
        self.selected = None
        self.mouseUp = False

    def clearSandbox(self):
        self.bodies = []
    
    def getLaunchingSpeed(self):
        tempMouse = ((self.mouse[0]-c.panx)/c.zoom,(self.mouse[1]-c.pany)/c.zoom)
        self.mouseUp = False
        while not self.mouseUp:
            pygame.draw.circle(WIN, (155,155,155), (tempMouse[0],tempMouse[1]), 12)
            self.selected.x = tempMouse[0]/SCALE
            self.selected.y = tempMouse[1]/SCALE
            self.selected.x_vel = (tempMouse[0]-(self.mouse[0]-c.panx)/c.zoom)*5
            self.selected.y_vel = (tempMouse[1]-(self.mouse[1]-c.pany)/c.zoom)*5
        g.bodies.append(self.selected)
        self.selected = None


class Camera:
    def __init__(self) -> None:
        self.zoom = 1
        self.zoomSize = 1
        self.panAcceleration = 0
        self.panx = 0
        self.pany = 0
        self.keyPressed = False
    def toggleObjects(self)->None:
        if self.zoomSize == 1:
            self.zoomSize = 0
        else:
            self.zoomSize = 1

class Object:
    def __init__(self,name="",x=0,y=0,radius=0,color=(),mass=0)-> None:
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        
        self.sun = False
        self.x_vel = 0
        self.y_vel = 0

    def draw(self,win)-> None:
        x = self.x * SCALE
        y = self.y * SCALE
        pygame.draw.circle(win, self.color, ((x+c.panx)*c.zoom,(y+c.pany)*c.zoom), self.radius*c.zoomSize)
    
    def attraction(self, other)-> float | float:
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y,distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

class Button:
    def __init__(self,x:int,y:int,width:int,height:int,color:tuple,screen:pygame.Surface,text=''):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.collided = False
        self.text = font.render(text, True, GRAY,(100,100,100) )
        
        
        self.screen = screen
        self.screenWidth = screen.get_width()
        self.screenHeight = screen.get_height()

    def draw(self,mouse:tuple):
        if self.x <= mouse[0] <= self.x+self.width and self.y <= mouse[1] <= self.y+self.height:
            self.collided = True
            pygame.draw.rect(WIN,(10,127,189),[self.x,self.y,self.width,self.height])
        else:
            self.collided = False
            pygame.draw.rect(WIN,(100,100,100),[self.x,self.y,self.width,self.height])

        WIN.blit(self.text,(self.x+(self.width-self.text.get_width())/2, self.y+self.height-self.text.get_height()))
        pygame.draw.circle(WIN, self.color, (self.x+self.width/2,self.y+self.height/2), 10)
    def clicked(self):
        if self.collided:
            g.clearSandbox()

class PlanetButton(Button):
    def __init__(self, x: int, y: int, width: int, height: int, color: tuple, value: Object, screen: pygame.Surface)-> None:
        super().__init__(x, y, width, height, color, screen)
        self.value = value
        self.text = font.render(self.value.name, True, GRAY,(100,100,100) )
    def draw(self,mouse:tuple)-> None:
        if self.x <= mouse[0] <= self.x+self.width and self.y <= mouse[1] <= self.y+self.height:
            self.collided = True
            pygame.draw.rect(WIN,(10,127,189),[self.x,self.y,self.width,self.height])
        else:
            self.collided = False
            pygame.draw.rect(WIN,(100,100,100),[self.x,self.y,self.width,self.height])

        WIN.blit(self.text,(self.x+(self.width-self.text.get_width())/2, self.y+self.height-self.text.get_height()))
        pygame.draw.circle(WIN, self.color, (self.x+self.width/2,self.y+self.height/2), 10)
    def clicked(self):
        if self.collided:
            return copy.copy(self.value)
        return None

    
c = Camera()
g = Game()


rocket_ship = Object(name="rocket", x= .5*AU, y=0, radius=6, color=WHITE, mass=137438.488)

neptune = Object(name='neptune',x=0.8*AU,y=0.4*AU,radius=13,color=(71,120,224),mass=1.024 * 10**26)
uranus = Object(name='uranus',x=0.1*AU,y=1.2*AU,radius=12,color=(167,221,240),mass=8.681 * 10**25)
saturn = Object(name='saturn',x=0.2*AU,y=2*AU,radius=14,color=(189,169,140),mass=5.683 * 10**26)
jupiter = Object(name='jupiter',x=.7*AU,y=1*AU,radius=17,color=(189,140,70),mass=1.89813 * 10**27)
mars = Object(name="mars", x=-0.3 * AU, y=0, radius=8, color=RED, mass=6.39 * 10**23)
earth = Object(name="earth",  x=5 * AU, y=2*AU, radius=10, color=BLUE, mass=5.9742 * 10**24)
venus = Object(name='venus', x=0.5*AU,y=0,radius=9,color=ORANGE,mass=4.867 * 10**24)
mercury = Object(name='mercury',x=1*AU,y=0,radius=6,color=GRAY,mass=3.28 * 10**23)
mars.y_vel = 80


n = PlanetButton(10,10,60,60,neptune.color,neptune,WIN)
u = PlanetButton(10,70,60,60,uranus.color,uranus,WIN)
s = PlanetButton(10,130,60,60,saturn.color,saturn,WIN)
j = PlanetButton(10,190,60,60,jupiter.color,jupiter,WIN)
m = PlanetButton(10,250,60,60,RED,mars,WIN)
e = PlanetButton(10,310,60,60,BLUE,earth,WIN)
v = PlanetButton(10,370,60,60,venus.color,venus,WIN)
my = PlanetButton(10,430,60,60,mercury.color,mercury,WIN)

clear = Button(10,490,60,60,WHITE,WIN,text='clear')


g.buttons = [n,u,s,j,m,e,v,my,clear]


run = True
clock = pygame.time.Clock()

counter = 0
while run:
    clock.tick(60)
    WIN.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:

            if g.selected != None and g.mouseUp:
                threading.Thread(target=g.getLaunchingSpeed).start()
            else:
                tempPos = g.mouse

            for button in g.buttons:
                if g.selected == None:
                    g.selected = button.clicked()
        if event.type == pygame.MOUSEBUTTONUP:
            g.mouseUp = True
        
        if event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                c.zoom += 0.01
                c.zoomSize += 0.01
            else:
                c.zoom -= 0.01
                c.zoomSize -= 0.01
    keys = pygame.key.get_pressed()
    c.panAcceleration += 0.1
    c.keyPressed = False
    if keys[pygame.K_w]:
        c.pany += 1+c.panAcceleration
        c.keyPressed = True
    if keys[pygame.K_s]:
        c.pany -= 1+c.panAcceleration
        c.keyPressed = True
    if keys[pygame.K_d]:
        c.panx -= 1+c.panAcceleration
        c.keyPressed = True
    if keys[pygame.K_a]:
        c.panx += 1+c.panAcceleration
        c.keyPressed = True
    if not c.keyPressed:
        c.panAcceleration = 0
    
            
    g.mouse = pygame.mouse.get_pos()
    for button in g.buttons:
        button.draw(g.mouse)

    for body in g.bodies:
        current_total_force_x = 0
        current_total_force_y = 0
        for other in g.bodies:
            if other != body:
                dx = (body.x*SCALE)-(other.x*SCALE)
                dy = (body.y*SCALE)-(other.y*SCALE)
                if abs(dx) < body.radius+other.radius and abs(dy) < body.radius+other.radius:
                    if body.mass > other.mass:
                        body.mass += other.mass
                        body.radius += math.floor(other.radius/8)
                        g.bodies.remove(other)
                    else:
                        other.mass += body.mass
                        other.radius += math.floor(body.radius/8)
                        g.bodies.remove(body) 

                force_x, force_y = body.attraction(other)
                current_total_force_x += force_x
                current_total_force_y += force_y

        body.x_vel += current_total_force_x / body.mass * TIMESTEP
        body.y_vel += current_total_force_y / body.mass * TIMESTEP

        body.x += body.x_vel * TIMESTEP
        body.y += body.y_vel * TIMESTEP
        body.draw(WIN)
    pygame.display.update()

pygame.quit()