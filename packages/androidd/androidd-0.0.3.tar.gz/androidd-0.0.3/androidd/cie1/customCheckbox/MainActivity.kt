package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.*

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val checkbox = findViewById<CheckBox>(R.id.checkboxCustom)
        val button = findViewById<Button>(R.id.btnCheck)

        button.setOnClickListener {
            val msg = if (checkbox.isChecked) "Subscribed!" else "Not Subscribed!"
            Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
        }
    }
}
