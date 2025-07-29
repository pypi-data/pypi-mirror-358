# Hack4u Academy Courses library

Biblioteca de Python para filtar por los cursos de hack4u

## Cursos disponibles

- Introduccion a linux \[15 horas\]
- Personalizacion de linux \[3 horas\]
- Introduccion al hacking \[53 horas\]
- Python ofensivo \[35 horas\]

## Instalacion
Instalando con el uso de 'pip3':
```python3
pip3 install hack4u
```

## Uso basico

### Listar los cursos

```python3
from hack4u import list_courses

for course in list_courses():
    print(course)
```

### Encontrar curso por su nombre

```python3
from hack4u import find_course_by_name

print(find_course_by_name("Introduccion al hacking"))
```

### Calcular duracion total de todos los cursos
```python3
from hack4u import total_duration

total_duration()
```


