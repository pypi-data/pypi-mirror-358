package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.Button
import android.widget.CheckBox
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val chkChocolate = findViewById<CheckBox>(R.id.chkChocolate)
        val chkSprinkles = findViewById<CheckBox>(R.id.chkSprinkles)
        val chkNuts = findViewById<CheckBox>(R.id.chkNuts)
        val btnShow = findViewById<Button>(R.id.btnShow)

        btnShow.setOnClickListener {
            val selected = mutableListOf<String>()
            if (chkChocolate.isChecked) selected.add("Chocolate")
            if (chkSprinkles.isChecked) selected.add("Sprinkles")
            if (chkNuts.isChecked) selected.add("Nuts")

            Toast.makeText(this, "Selected: ${selected.joinToString()}", Toast.LENGTH_SHORT).show()
        }
    }
}
