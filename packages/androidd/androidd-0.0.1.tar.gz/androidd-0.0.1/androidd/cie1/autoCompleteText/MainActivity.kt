package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val countries = arrayOf("India", "Indonesia", "Italy", "Iceland", "Iran")
        val adapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, countries)

        val autoCompleteTextView = findViewById<AutoCompleteTextView>(R.id.autoCompleteTextView)
        autoCompleteTextView.setAdapter(adapter)
    }
}
