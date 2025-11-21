FROM node:18-alpine

WORKDIR /app

# Копируем package.json отдельно для кэширования
COPY package*.json ./
RUN npm install

# Копируем остальные файлы
COPY . .

# Создаем необходимые файлы если их нет
RUN if [ ! -f tsconfig.json ]; then \
      npx create-react-app . --template typescript --skip-git; \
    fi

EXPOSE 3000

CMD ["npm", "run", "dev"]