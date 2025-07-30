package com.example.labexam_01

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.CheckBox
import android.widget.TextView
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    fun calculateTotal(view: View) {
        val book1 = findViewById<CheckBox>(R.id.book1)
        val book2 = findViewById<CheckBox>(R.id.book2)
        val book3 = findViewById<CheckBox>(R.id.book3)
        val result = findViewById<TextView>(R.id.tvResult)

        var total = 0

        if (book1.isChecked) total += 120
        if (book2.isChecked) total += 150
        if (book3.isChecked) total += 200

        val finalAmount = if (total > 300) total * 0.9 else total.toDouble()

        if (total > 0) {
            val discountText = if (total > 300) " (10% discount applied)" else ""
            result.text = "Total: ₹${"%.2f".format(finalAmount)}$discountText"
        } else {
            Toast.makeText(this, "Please select at least one book", Toast.LENGTH_SHORT).show()
        }
    }
}
