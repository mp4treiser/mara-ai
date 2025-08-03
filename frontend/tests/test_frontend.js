#!/usr/bin/env node
/**
 * Простой тест для проверки работы фронтенда
 */

console.log('🧪 Тестирование фронтенда...\n');

// Проверяем наличие необходимых файлов
const fs = require('fs');
const path = require('path');

const requiredFiles = [
  'src/api/auth.ts',
  'src/contexts/AuthContext.tsx',
  'src/components/ProtectedRoute.tsx',
  'src/pages/LoginPage.tsx',
  'src/pages/RegisterPage.tsx',
  'src/pages/ProfilePage.tsx',
  'src/app.tsx',
  'package.json'
];

console.log('📁 Проверка структуры файлов:');
let allFilesExist = true;

requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`   ✅ ${file}`);
  } else {
    console.log(`   ❌ ${file} - НЕ НАЙДЕН`);
    allFilesExist = false;
  }
});

console.log('\n🔧 Проверка package.json:');
try {
  const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
  
  const requiredDeps = ['react', 'react-dom', 'react-router-dom'];
  const requiredDevDeps = ['typescript', 'webpack'];
  
  console.log('   Зависимости:');
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`     ✅ ${dep}: ${packageJson.dependencies[dep]}`);
    } else {
      console.log(`     ❌ ${dep} - НЕ НАЙДЕН`);
      allFilesExist = false;
    }
  });
  
  console.log('   Dev зависимости:');
  requiredDevDeps.forEach(dep => {
    if (packageJson.devDependencies && packageJson.devDependencies[dep]) {
      console.log(`     ✅ ${dep}: ${packageJson.devDependencies[dep]}`);
    } else {
      console.log(`     ❌ ${dep} - НЕ НАЙДЕН`);
      allFilesExist = false;
    }
  });
  
  console.log('   Скрипты:');
  if (packageJson.scripts) {
    if (packageJson.scripts.start) {
      console.log(`     ✅ start: ${packageJson.scripts.start}`);
    } else {
      console.log('     ❌ start - НЕ НАЙДЕН');
      allFilesExist = false;
    }
    
    if (packageJson.scripts.build) {
      console.log(`     ✅ build: ${packageJson.scripts.build}`);
    } else {
      console.log('     ❌ build - НЕ НАЙДЕН');
      allFilesExist = false;
    }
  }
  
} catch (error) {
  console.log(`   ❌ Ошибка чтения package.json: ${error.message}`);
  allFilesExist = false;
}

console.log('\n🔌 Проверка API конфигурации:');
try {
  const authFile = fs.readFileSync(path.join(__dirname, 'src/api/auth.ts'), 'utf8');
  
  if (authFile.includes('API_BASE_URL')) {
    console.log('   ✅ API_BASE_URL настроен');
  } else {
    console.log('   ❌ API_BASE_URL не найден');
    allFilesExist = false;
  }
  
  if (authFile.includes('authAPI')) {
    console.log('   ✅ authAPI экспортирован');
  } else {
    console.log('   ❌ authAPI не найден');
    allFilesExist = false;
  }
  
  if (authFile.includes('login')) {
    console.log('   ✅ Метод login реализован');
  } else {
    console.log('   ❌ Метод login не найден');
    allFilesExist = false;
  }
  
  if (authFile.includes('register')) {
    console.log('   ✅ Метод register реализован');
  } else {
    console.log('   ❌ Метод register не найден');
    allFilesExist = false;
  }
  
  if (authFile.includes('getProfile')) {
    console.log('   ✅ Метод getProfile реализован');
  } else {
    console.log('   ❌ Метод getProfile не найден');
    allFilesExist = false;
  }
  
} catch (error) {
  console.log(`   ❌ Ошибка чтения auth.ts: ${error.message}`);
  allFilesExist = false;
}

console.log('\n🎯 Проверка маршрутизации:');
try {
  const appFile = fs.readFileSync(path.join(__dirname, 'src/app.tsx'), 'utf8');
  
  if (appFile.includes('AuthProvider')) {
    console.log('   ✅ AuthProvider подключен');
  } else {
    console.log('   ❌ AuthProvider не подключен');
    allFilesExist = false;
  }
  
  if (appFile.includes('ProtectedRoute')) {
    console.log('   ✅ ProtectedRoute подключен');
  } else {
    console.log('   ❌ ProtectedRoute не подключен');
    allFilesExist = false;
  }
  
  if (appFile.includes('/profile')) {
    console.log('   ✅ Маршрут /profile настроен');
  } else {
    console.log('   ❌ Маршрут /profile не найден');
    allFilesExist = false;
  }
  
} catch (error) {
  console.log(`   ❌ Ошибка чтения app.tsx: ${error.message}`);
  allFilesExist = false;
}

console.log('\n📋 Результат:');
if (allFilesExist) {
  console.log('🎉 Все проверки пройдены успешно!');
  console.log('\n🚀 Для запуска фронтенда выполните:');
  console.log('   npm install');
  console.log('   npm start');
  console.log('\n🔗 Фронтенд будет доступен по адресу: http://localhost:8080');
  console.log('\n⚠️  Убедитесь, что бэкенд запущен на http://localhost:8000');
} else {
  console.log('❌ Некоторые проверки не пройдены');
  console.log('Проверьте структуру файлов и зависимости');
}

console.log('\n📝 Следующие шаги:');
console.log('1. Запустите бэкенд: cd backend && uvicorn main:app --reload');
console.log('2. Запустите фронтенд: cd frontend && npm start');
console.log('3. Откройте http://localhost:8080 в браузере');
console.log('4. Попробуйте зарегистрироваться и войти в систему'); 