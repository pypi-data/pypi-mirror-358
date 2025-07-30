package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btn = findViewById<Button>(R.id.btnCustomToast)
        btn.setOnClickListener {
            showCustomToast()
        }
    }

    private fun showCustomToast() {
        val inflater: LayoutInflater = layoutInflater
        val view: View = inflater.inflate(R.layout.custom_toast, null)

        val text = view.findViewById<TextView>(R.id.toastText)
        text.text = "Hello from Custom Toast!"

        val toast = Toast(applicationContext)
        toast.duration = Toast.LENGTH_SHORT
        toast.view = view
        toast.show()
    }
}

