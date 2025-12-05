#version 330 core

in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

// положение камеры
uniform vec3 viewPos;

// параметры источника света
uniform vec3 lightPos;
uniform vec3 lightColor;

// параметры материала
uniform vec3 matAmbient;
uniform vec3 matDiffuse;
uniform vec3 matSpecular;
uniform float shininess;

void main()
{
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);

    float diff = max(dot(norm, lightDir), 0.0);

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);

    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);

    vec3 ambient = matAmbient * lightColor;
    vec3 diffuse = matDiffuse * diff * lightColor;
    vec3 specular = matSpecular * spec * lightColor;

    FragColor = vec4(ambient + diffuse + specular, 1.0);
}
