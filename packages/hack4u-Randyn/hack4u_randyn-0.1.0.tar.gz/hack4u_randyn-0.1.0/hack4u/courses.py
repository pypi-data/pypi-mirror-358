class Course:
    def __init__(self, name, duration, link):
        self.name = name
        self.duration = duration
        self.link = link

    def __str__(self):
        return f"{self.name} [{self.duration} horas] ({self.link})"

    def __repr__(self):
        return f"{self.name} [{self.duration} horas] ({self.link})"

courses = [
    Course("Introduccion a linux", 15, "https://hack4u.io/cursos/introduccion-a-linux/"),
    Course("Personalizacion de linux", 3,"https://hack4u.io/cursos/personalizacion-de-entorno-en-linux/"),
    Course("Introduccion al hacking", 53,"https://hack4u.io/cursos/introduccion-al-hacking/"),
    Course("Python ofensivo", 35,"https://hack4u.io/cursos/python-ofensivo/")
]

def list_courses():
    for i in courses:
        print(i)

def find_course_by_name(name):
    for i in courses:
        if name.lower() == i.name.lower():
            return i
    return None
