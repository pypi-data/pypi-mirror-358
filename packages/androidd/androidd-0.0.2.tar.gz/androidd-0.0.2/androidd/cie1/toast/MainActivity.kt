package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.Button
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnToast = findViewById<Button>(R.id.btnToast)
        btnToast.setOnClickListener {
            Toast.makeText(this, "Hello from Toast!", Toast.LENGTH_SHORT).show()
        }
    }
}
