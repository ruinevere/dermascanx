<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use GuzzleHttp\Client;
use Exception;

class SkinDiseaseController extends Controller
{
    public function predict(Request $request)
    {
        $request->validate([
            'image' => 'required|image|mimes:jpeg,png,jpg|max:2048',
        ]);

        try {
            $client = new Client();

            $response = $client->post('http://127.0.0.1:5000/predict', [
                'multipart' => [
                    [
                        'name'     => 'image',
                        'contents' => fopen($request->file('image')->getPathname(), 'r'),
                        'filename' => $request->file('image')->getClientOriginalName(),
                    ]
                ]
            ]);

            $body = json_decode($response->getBody(), true);
            return view('predict', ['result' => $body]);

        } catch (Exception $e) {
            return back()->with('error', 'Prediction failed: ' . $e->getMessage());
        }
    }
}
