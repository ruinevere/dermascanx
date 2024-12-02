<?php

// use Illuminate\Support\Facades\Route;

// // Route::get('/', function () {
// //     return view('welcome');
// // });

// Route::get('/WebProg', function (){
//     echo '<h1>Hello</h1>';
//     echo '<p>testing</p>';
// });

use App\Http\Controllers\SkinDiseaseController;

Route::get('/WebProg', function () {
    return view('predict');
});

Route::post('/WebProg/predict', [SkinDiseaseController::class, 'predict']);

